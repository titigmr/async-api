import { AsyncWorkerRunner, Infinite, IncomingMessage, TaskInterface } from './worker';

class ExampleTask implements TaskInterface {
  async execute(incomingMessage: IncomingMessage, progress: (p: number) => Promise<void>) {
    console.log(`Starting task ${incomingMessage.task_id} with body:`, incomingMessage.body);

    const { sleep, mustSucceed } = incomingMessage.body;

    for (let i = 1; i <= sleep; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await progress(i / sleep);
    }
    if (!mustSucceed) {
      throw Error("Arggggh")
    }
    return { hellow: "world" };
  }
}

async function main() {
  const runner = new AsyncWorkerRunner(
    'amqp://kalo:kalo@127.0.0.1:5672',
    'ts_in_queue',
    'ts_out_queue',
    () => new ExampleTask(),
    new Infinite(3), // or new OnShot()
    { host: '0.0.0.0', port: 18181 },
  );

  await runner.start();
}

main();