#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <json/json.h>

int main()
{
    const int MAX_RETRIES = 5;
    const std::chrono::seconds RETRY_INTERVAL(5);
    const std::string AMQP_URL = "rabbitmq";
    const std::string EXCHANGE_NAME_SUB = "logs2";
    const std::string EXCHANGE_NAME_PUB = "value1_exchange";
    const int TIMEOUT_MS = 5000;

    AmqpClient::Channel::ptr_t channel;
    int retryCount = 0;

    while (retryCount < MAX_RETRIES)
    {
        try
        {
            channel = AmqpClient::Channel::Create(AMQP_URL);
            if (!channel)
            {
                std::cerr << "Failed to connect after " << MAX_RETRIES << " retries." << std::endl;
            }
            break;
        }
        catch (const AmqpClient::AmqpLibraryException &e)
        {
            std::cerr << "Connection failed: " << e.what() << std::endl;
            retryCount++;
            std::this_thread::sleep_for(RETRY_INTERVAL);
        }
    }

    if (!channel)
    {
        std::cerr << "Failed to connect after " << MAX_RETRIES << " retries." << std::endl;
        return 1;
    }

    channel->DeclareExchange(EXCHANGE_NAME_SUB, AmqpClient::Channel::EXCHANGE_TYPE_FANOUT, true, true, false);
    std::string queue_name = channel->DeclareQueue("", false, true, true, true);
    channel->BindQueue(queue_name, EXCHANGE_NAME_SUB, "");

    std::cout << "Waiting for messages. To exit press CTRL+C" << std::endl;
    auto consumer_tag = channel->BasicConsume(queue_name, "", true, false, false, 1);

    int count = 0;

    channel->DeclareExchange(EXCHANGE_NAME_PUB, AmqpClient::Channel::EXCHANGE_TYPE_FANOUT, false, true, false);

    // try {
    //     channel->DeclareExchange(EXCHANGE_NAME_PUB, AmqpClient::Channel::EXCHANGE_TYPE_FANOUT, true, true, false);
    // } catch (const AmqpClient::AmqpResponseLibraryException &e) {
    //     std::cerr << "Failed to declare exchange: " << e.what() << std::endl;
    //     return 1;
    // }

    while (true)
    {
        AmqpClient::Envelope::ptr_t envelope;
        bool received = channel->BasicConsumeMessage(consumer_tag, envelope, TIMEOUT_MS);

        if (received && envelope)
        {
            std::string message = envelope->Message()->Body();
            std::cout << "Received message: " << message << std::endl;
            channel->BasicAck(envelope);

            // Json::Value sensor_data;
            // std::istringstream(message) >> sensor_data;

            Json::Value root;
            std::istringstream(message) >> root;
            if (root.isArray() && !root.empty())
            {
                Json::Value sensor_data = root[0];

                int16_t sensor0 = (int16_t)sensor_data["sensor0"].asInt();
                int16_t sensor1 = (int16_t)sensor_data["sensor1"].asInt();

                std::cout << "sensor0: " << sensor0 << std::endl;
                std::cout << "sensor1: " << sensor1 << std::endl;

                // Json::Value value_pub;
                // value_pub["value1"] = sensor0;

                Json::StreamWriterBuilder writer;
                // std::string json_message = Json::writeString(writer, value_pub);

                auto value_pub = Json::Value(Json::arrayValue);
                value_pub.append(count);
                value_pub.append(count);
                std::string json_message = Json::writeString(writer, value_pub);

                channel->BasicPublish(
                    EXCHANGE_NAME_PUB,
                    "",
                    AmqpClient::BasicMessage::Create(json_message));

                std::cout << "Message sent: " << json_message << std::endl;
            }
            else
            {
                std::cerr << "Received message is not a valid JSON array or is empty." << std::endl;
            }
            count++;
        }
        else
        {
            std::cout << "No message received within timeout period." << std::endl;
        }
    }

    return 0;
}
