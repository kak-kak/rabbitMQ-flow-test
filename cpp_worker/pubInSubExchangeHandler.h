#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <vector>
#include <json/json.h>

class PubInSubExchangeHandler
{
public:
    PubInSubExchangeHandler(const std::string &exchange_name_sub, const std::string &exchange_name_pub,
                            std::function<void(AmqpClient::Channel::ptr_t, AmqpClient::Envelope::ptr_t, State &)> callback, State &state)
        : exchange_name_sub(exchange_name_sub), exchange_name_pub(exchange_name_pub), callback(callback), state(state)
    {
        try_connect();
        register_sub_exchange();
        register_pub_exchange();
        start_sub();
    }

private:
    struct State
    {
        std::vector<int> sensor0_values;
        int val;
    };

    std::string exchange_name_sub;
    std::string exchange_name_pub;
    std::function<void(AmqpClient::Channel::ptr_t, AmqpClient::Envelope::ptr_t, State &)> callback;
    State &state;
    AmqpClient::Channel::ptr_t channel;
    std::string queue_name;
    std::string consumer_tag;

    void try_connect()
    {
        const int MAX_RETRIES = 5;
        const std::chrono::seconds RETRY_INTERVAL(5);
        int retryCount = 0;

        while (retryCount < MAX_RETRIES)
        {
            try
            {
                channel = AmqpClient::Channel::Create("rabbitmq");
                if (!channel)
                {
                    std::cerr << "Failed to connect after " << MAX_RETRIES << " retries." << std::endl;
                    exit(1);
                }
                break; // Connection successful
            }
            catch (const AmqpClient::AmqpLibraryException &e)
            {
                std::cerr << "Connection attempt " << retryCount + 1 << "/" << MAX_RETRIES << " failed: " << e.what() << std::endl;
                retryCount++;
                std::this_thread::sleep_for(RETRY_INTERVAL);
            }
        }

        if (!channel)
        {
            std::cerr << "Failed to connect to RabbitMQ after several attempts." << std::endl;
            exit(1);
        }
    }

    void register_sub_exchange()
    {
        channel->DeclareExchange(exchange_name_sub, AmqpClient::Channel::EXCHANGE_TYPE_FANOUT, true, true, false);
        queue_name = channel->DeclareQueue("", false, true, true, true);
        channel->BindQueue(queue_name, exchange_name_sub, "");
    }

    void register_pub_exchange()
    {
        channel->DeclareExchange(exchange_name_pub, AmqpClient::Channel::EXCHANGE_TYPE_FANOUT, true, true, false);
        std::cout << "Waiting for messages. To exit press CTRL+C" << std::endl;
    }

    void start_sub()
    {
        consumer_tag = channel->BasicConsume(queue_name, "", true, false, false, 1);
        while (true)
        {
            AmqpClient::Envelope::ptr_t envelope;
            bool received = channel->BasicConsumeMessage(consumer_tag, envelope, 5000);

            if (received && envelope)
            {
                callback(channel, envelope, state);
            }
            else
            {
                std::cout << "No message received within timeout period." << std::endl;
            }
        }
    }
};

void message_callback(AmqpClient::Channel::ptr_t channel, AmqpClient::Envelope::ptr_t envelope, PubInSubExchangeHandler::State &state)
{
    try
    {
        std::string body_str = envelope->Message()->Body();
        Json::Value sensor_data;
        std::istringstream(body_str) >> sensor_data;
        std::string date = getCurrentDateTime();
        std::cout << "Received sensor data " << date << ": " << sensor_data << std::endl;

        state.sensor0_values.push_back(sensor_data[0]["sensor0"].asInt());
        if (state.sensor0_values.size() > 10)
        {
            state.sensor0_values.erase(state.sensor0_values.begin());
        }

        if (state.sensor0_values.size() == 10)
        {
            Json::Value value1_message;
            value1_message["value1"] = state.val;
            state.val++;

            Json::StreamWriterBuilder writer;
            std::string message_str = Json::writeString(writer, value1_message);

            channel->BasicPublish(exchange_name_pub, "", AmqpClient::BasicMessage::Create(message_str),
                                  AmqpClient::BasicProperties().ContentType("application/json"));
            std::cout << "Published value1: " << message_str << std::endl;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to process message: " << e.what() << std::endl;
    }
}

int main()
{
    PubInSubExchangeHandler::State state = {.sensor0_values = {}, .val = 0};
    PubInSubExchangeHandler handler("logs2", "value1_exchange", message_callback, state);
    return 0;
}
