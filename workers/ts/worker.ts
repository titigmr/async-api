// worker.ts
import amqplib from 'amqplib';
import type { Channel, ConsumeMessage, ChannelModel } from 'amqplib';
import { createServer } from 'http';
import { hostname } from 'os';

type ProgressCallbackAsync = (progress: number) => Promise<void>;

export class IncomingMessage {
  constructor(public task_id: string, public body: any) {}
}

export interface TaskInterface {
  execute(incomingMessage: IncomingMessage, progress: ProgressCallbackAsync): Promise<any>;
}

export class OnShot {}

export class Infinite {
  constructor(public concurrency: number = 1) {}
}

export type WorkerMode = OnShot | Infinite;

export class SendException extends Error {}
export class IncomingMessageException extends Error {}
export class TaskException extends Error {}

export interface HealthCheckConfig {
  host: string;
  port: number;
}

export class HealthCheckServer {
  constructor(private host: string, private port: number) {}

  start() {
    const server = createServer((req, res) => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok' }));
    });
    server.listen(this.port, this.host);
  }
}

export class AsyncWorkerRunner {
  private oneShot: boolean = false;
  private nbrAsyncTask: number = 1;

  constructor(
    private amqpUrl: string,
    private amqpInQueue: string,
    private amqpOutQueue: string,
    private taskProvider: () => TaskInterface,
    private workerMode: WorkerMode,
    private healthCheckConfig?: HealthCheckConfig
  ) {
    if (workerMode instanceof OnShot) {
      this.oneShot = true;
    }
    if (workerMode instanceof Infinite) {
      this.oneShot = false;
      this.nbrAsyncTask = workerMode.concurrency;
    }
  }

  async start() {
    console.log("🛜 Connecting to RabbitMQ...");

    const connection = await this.waitForConnection();
    const channel = await connection.createChannel();
    await channel.prefetch(this.nbrAsyncTask);
    await channel.assertQueue(this.amqpInQueue, { durable: true });

    console.log("🤗 Successfully connected.");

    if (this.healthCheckConfig) {
      const healthCheck = new HealthCheckServer(this.healthCheckConfig.host, this.healthCheckConfig.port);
      healthCheck.start();
    }

    process.on('SIGINT', () => this.stop());
    process.on('SIGTERM', () => this.stop());

    await channel.consume(this.amqpInQueue, (msg) => {
      if (msg) this.processMessage(msg, channel);
    });
  }

  private parseIncomingMessage(message: string): IncomingMessage {
    let dictBody: any;
    try {
      dictBody = JSON.parse(message);
    } catch {
      throw new IncomingMessageException("Invalid JSON");
    }

    if (!dictBody.task_id || typeof dictBody.task_id !== 'string') {
      throw new IncomingMessageException("Missing or invalid task_id");
    }

    if (!dictBody.data || typeof dictBody.data !== 'object' || !dictBody.data.body) {
      throw new IncomingMessageException("Missing data.body field");
    }

    return new IncomingMessage(dictBody.task_id, dictBody.data.body);
  }

  private async processMessage(msg: ConsumeMessage, channel: Channel) {
    let taskId: string | null = null;
    try {
      const body = msg.content.toString();
      const incomingMessage = this.parseIncomingMessage(body);
      taskId = incomingMessage.task_id;

      await this.sendStartMessage(channel, taskId);
      const result = await this.launchTask(incomingMessage, taskId);
      console.log("Task: "+taskId+" ended.")
      await this.sendSuccessMessage(channel, taskId, result);
      channel.ack(msg);
    } catch (e) {
      if (e instanceof IncomingMessageException) {
        console.log("Invalid incoming message:", e);
        channel.ack(msg);
      } else if (e instanceof SendException) {
        console.log("Unable to send message:", e);
      } else if (e instanceof TaskException) {
        console.log("Task error:", e.message);
        try {
          if (taskId) {
            await this.sendFailureMessage(channel, taskId, e.message);
            channel.ack(msg);
          }
        } catch {
          console.log("Unable to send failure message.");
        }
      }
    }

    if (this.oneShot) this.stop();
  }

  private async launchTask(incoming: IncomingMessage, taskId: string): Promise<any> {
    const task = this.taskProvider();

    const progressCallback = async (progress: number) => {
      await this.sendProgressMessage(taskId, progress);
    };

    try {
      console.log("Running async task");
      return await task.execute(incoming, progressCallback);
    } catch (e: any) {
      throw new TaskException(e.message);
    }
  }

  private async sendStartMessage(channel: Channel, taskId: string) {
    const payload = {
      task_id: taskId,
      data: { message_type: "started", hostname: hostname() },
    };
    await this.sendMessage(channel, payload);
  }

  private async sendSuccessMessage(channel: Channel, taskId: string, result: any) {
    const payload = {
      task_id: taskId,
      data: { message_type: "success", response: result },
    };
    await this.sendMessage(channel, payload);
  }

  private async sendProgressMessage(taskId: string, progress: number) {
    const connection = await this.waitForConnection();
    const channel = await connection.createChannel();
    const payload = {
      task_id: taskId,
      data: { message_type: "progress", progress },
    };
    await this.sendMessage(channel, payload);
    await channel.close();
    await connection.close();
  }

  private async sendFailureMessage(channel: Channel, taskId: string, errorMessage: string) {
    const payload = {
      task_id: taskId,
      data: { message_type: "failure", error_message: errorMessage },
    };
    await this.sendMessage(channel, payload);
  }

  private async sendMessage(channel: Channel, data: any) {
    try {
      const buffer = Buffer.from(JSON.stringify(data));
      await channel.assertQueue(this.amqpOutQueue, { durable: true });
      await channel.sendToQueue(this.amqpOutQueue, buffer);
    } catch (e: any) {
      throw new SendException(e.message);
    }
  }

  stop() {
    console.log("💥 Stop signal received.")
    process.kill(process.pid,"SIGKILL")
  }

  private async waitForConnection(): Promise<amqplib.ChannelModel> {
    while (true) {
      try {
        return await amqplib.connect(this.amqpUrl);
      } catch (e: any) {
        console.log(`Connection error: ${e.message}. Retrying in 5s...`);
        await new Promise((resolve) => setTimeout(resolve, 5000));
      }
    }
  }
}
