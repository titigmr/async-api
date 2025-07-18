const amqp = require('amqplib');
const os = require('os');

//------------------------
// CONFIGURATION
//------------------------
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost:5672';
const RABBITMQ_USER = process.env.RABBITMQ_USER || 'kalo';
const RABBITMQ_PASSWORD = process.env.RABBITMQ_PASSWORD || 'kalo';
const LISTENER_COUNT = Number(process.env.LISTENER_COUNT) || 5;

const IN_QUEUE_NAME = process.env.IN_QUEUE_NAME || 'example';
const OUT_QUEUE_NAME = process.env.OUT_QUEUE_NAME ||'example_out';

//------------------------
// FRAMEWORK
//------------------------

// Utilitaire d'envoie de message (Started/End)
class MessageSender {
    constructor(rabbitmqUrl, rabbitmqUser, rabbitmqPassword, outQueue) {
        this.rabbitmqUrl = rabbitmqUrl;
        this.rabbitmqUser = rabbitmqUser;
        this.rabbitmqPassword = rabbitmqPassword;
        this.outQueue = outQueue;
    }

    async _sendMessage(message) {
        const opt = { credentials: amqp.credentials.plain(this.rabbitmqUser, this.rabbitmqPassword) };
        const connection = await amqp.connect(this.rabbitmqUrl,opt);

        const channel = await connection.createChannel();
        await channel.assertQueue(this.outQueue, { durable: true });

        channel.sendToQueue(this.outQueue, Buffer.from(JSON.stringify(message)), {
            persistent: true,
        });

        console.log("Message envoyé:", message);
        await channel.close();
        await connection.close();
    }

    async sendStartMessage(task_id) {
        await this._sendMessage({
            task_id: task_id,
            data: {
                message_type: "started",
                hostname: os.hostname()
            }
        })
    }

    async sendSuccessMessage(task_id, result) {
        await this._sendMessage({
            task_id: task_id,
            data: {
                message_type: "success",
                response: result
            }
        }) 
    }

    async sendFailureMessage(task_id, cause) {
        await this._sendMessage({
            task_id: task_id,
            data: {
                message_type: "failure",
                error_message: cause
            }
        }) 
    }
}

// Consumer et exécution des tâches
class TaskManager {
    constructor(rabbitmqUrl, rabbitmqUser, rabbitmqPassword,inQueue, outQueue, parallelism, taskFactory) {
        this.rabbitmqUrl = rabbitmqUrl;
        this.rabbitmqUser = rabbitmqUser;
        this.rabbitmqPassword = rabbitmqPassword;
        this.inQueue = inQueue;
        this.outQueue = outQueue;
        this.parallelism = parallelism;
        this.taskFactory = taskFactory;
        // Etat interne
        this.channels = [];
        this.inFlightMessages = new Map(); // Map(channel -> msg)
        this.isShuttingDown = false;
        this.messageSender = new MessageSender(rabbitmqUrl, rabbitmqUser, rabbitmqPassword, outQueue);
    }

    async start() {
        const opt = { credentials: amqp.credentials.plain(this.rabbitmqUser, this.rabbitmqPassword) };
        const connection = await amqp.connect(this.rabbitmqUrl,opt);

        // Gestion SIGTERM
        process.on('SIGTERM', async () => {
            await this.shutdown(connection);
        });
        process.on('SIGINT', async () => {
            await this.shutdown(connection);
        });


        for (let channelIndex = 0; channelIndex < this.parallelism; channelIndex++) {
            const channel = await connection.createChannel();
            this.channels.push(channel);

            await channel.assertQueue(this.inQueue, { durable: true });
            channel.prefetch(1);

            console.log(`[Listener ${channelIndex}] En attente de messages...`);

            channel.consume(
                this.inQueue,
                async (msg) => { this.onMessage(channelIndex,msg) },
                { noAck: false }
            );
        }
    }

    async onMessage(channelIndex,msg) {
        let channel = this.channels[channelIndex];
        this.inFlightMessages.set(channel, msg); // suivi du msg en cours

        const content = msg.content.toString();
        console.log(`[Listener ${channelIndex}] Reçu : ${content}`);
        const submissionMessage = this.parseSubmissionMessage(content);

        try {
            if (submissionMessage) {
                console.log(`[Listener ${channelIndex}] Submission : `,submissionMessage);
                try {
                    await this.messageSender.sendStartMessage(submissionMessage.task_id);
                    let task = this.taskFactory();
                    let result = await task.run(submissionMessage.data.body);
                    await this.messageSender.sendSuccessMessage(submissionMessage.task_id,result);
                } catch (err) {
                    await this.messageSender.sendFailureMessage(submissionMessage.task_id,err);
                }
            } else {
                console.error(`[Listener ${channelIndex}] Message invalide : ${content}`);
            }
        } catch (err) {
            console.error(`[Listener ${channelIndex}] Erreur :`, err);
        } finally {
            // Dans tous les cas on ACK!
            channel.ack(msg);
            this.inFlightMessages.delete(channel);
        }
    }

    parseSubmissionMessage(content) {
        try {
            let json = JSON.parse(content); 
            if (json.task_id && json.data && json.data.message_type && json.data.body) {
                return json;
            } else {
                return null;
            }
        } catch (err) {
            return null;
        }
    }

    async shutdown(connection) {
        // Parfois le signal arrive 2 fois.
        if (this.isShuttingDown) {
            return;
        }
        console.log('SIGTERM reçu. Nettoyage en cours...');
        this.isShuttingDown=true;

        // Arret des channels sans message en cours.
        // On ne veut pas qu'un channel en attente
        // puisse capter un message lors de l'arret
        // d'un autre listener (requeue)
        for (const channelIndex in this.channels) {
            let channel = this.channels[channelIndex];
            const msg = this.inFlightMessages.get(channel);
            if (!msg) {
                try {
                    console.log(`Fermeture du channel ${channelIndex}`);
                    await channel.close();
                } catch (err) {
                    console.error(`[!] Échec de fermeture du channel ${channelIndex}`, err);
                }
            }
        }
        // Arret des channels en cours de traitement
        for (const channelIndex in this.channels) {
            let channel = this.channels[channelIndex];
            const msg = this.inFlightMessages.get(channel);
            if (msg) {
                console.log(`Message en cours sur le channel ${channelIndex}, nack et requeue`);
                try {
                    channel.nack(msg, false, true); // requeue = true
                } catch (err) {
                    console.error(`[!] Échec du nack sur le channel ${channelIndex}`, err);
                }

                try {
                    await channel.close();
                } catch (err) {
                    console.error(`[!] Échec de fermeture du channel ${channelIndex}`, err);
                }
            }
        }

        try {
            await connection.close();
            console.log('[✓] Connexion RabbitMQ fermée.');
        } catch (err) {
            console.error('[!] Échec fermeture connexion', err);
        }
        process.exit(0);
    }
}

function sleepMs(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


//------------------------
// IMPLEMENTATION DE LA TACHE
//------------------------
class MyTask {
    constructor(){}
    async run({ sleep, mustSucceed }) {
        if (mustSucceed) {
            for (var i = 0; i < sleep; i++) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            return { hello: "world" }
        } else {
            throw "Argh!"
        }
    }
}

//------------------------
// EXECUTION
//------------------------
let taskManager = new TaskManager(
    RABBITMQ_URL,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    IN_QUEUE_NAME,
    OUT_QUEUE_NAME,
    LISTENER_COUNT,
    () => new MyTask()
);

taskManager.start().catch((err) => {
    console.error('[!] Erreur de démarrage', err);
    process.exit(1);
});

/* exemple de message:
{
  "task_id": "089373b8-1691-4462-8f78-25e3af1a1c6b",
  "data": { "message_type": "submission", "body": { "sleep": 10, "mustSucceed": true} }
}
*/
