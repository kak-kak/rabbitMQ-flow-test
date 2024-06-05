package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/streadway/amqp"
)

type SensorData struct {
	Sensor0 int16 `json:"sensor0"`
	Sensor1 int16 `json:"sensor1"`
}

func main() {
	const maxRetries = 5
	const retryInterval = 5 * time.Second
	exchangeName := "logs2"
	amqpURL := "amqp://rabbitmq"

	var conn *amqp.Connection
	var err error

	for i := 0; i < maxRetries; i++ {
		conn, err = amqp.Dial(amqpURL)
		if err == nil {
			break
		}
		log.Printf("Connection attempt %d/%d failed: %v", i+1, maxRetries, err)
		time.Sleep(retryInterval)
	}

	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ after %d attempts: %v", maxRetries, err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Failed to open a channel: %v", err)
	}
	defer ch.Close()

	err = ch.ExchangeDeclare(
		exchangeName, // name
		"fanout",     // type
		true,         // durable
		false,        // auto-deleted
		false,        // internal
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		log.Fatalf("Failed to declare an exchange: %v", err)
	}

	for i := 0; i < 10000; i++ {
		currentSecond := int16(time.Now().Second())
		data := []SensorData{
			{Sensor0: currentSecond, Sensor1: currentSecond},
		}

		body, err := json.Marshal(data)
		if err != nil {
			log.Fatalf("Failed to marshal sensor data: %v", err)
		}

		err = ch.Publish(
			exchangeName, // exchange
			"",           // routing key
			false,        // mandatory
			false,        // immediate
			amqp.Publishing{
				ContentType: "application/json",
				Body:        body,
				Expiration:  "20",
			})
		if err != nil {
			log.Fatalf("Failed to publish a message: %v", err)
		}
		date := time.Now().Format("2006-01-02 15:04:05.000")
		fmt.Printf("Time: %s Message %d sent: %s\n", date, i, body)
		time.Sleep(1 * time.Second)
	}
}
