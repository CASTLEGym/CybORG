#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <time.h>

#define DEFAULT_PORT 5001
#define MAX_IP_ADDRESS_LENGTH 16

int main(int argc, char *argv[]) {
  int port = DEFAULT_PORT;
  int listenfd, connfd;
  struct sockaddr_in server_addr, client_addr;
  socklen_t client_addr_len;
  time_t current_time;
  struct tm *time_info;
  char ip_address[MAX_IP_ADDRESS_LENGTH];
  FILE *log_file;

  // Parse optional port number from command line
  if (argc > 2) {
    fprintf(stderr, "Usage: %s [port]\n", argv[0]);
    return 1;
  }
  if (argc == 2) {
    port = atoi(argv[1]);
    if (port <= 0) {
      fprintf(stderr, "Invalid port number: %s\n", argv[1]);
      return 1;
    }
  }

  // Create socket
  listenfd = socket(AF_INET, SOCK_STREAM, 0);
  if (listenfd == -1) {
    perror("socket");
    return 1;
  }

  // Set socket options (reuse address)
  int reuse = 1;
  if (setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(int)) == -1) {
    perror("setsockopt");
    return 1;
  }

  // Bind socket
  memset(&server_addr, 0, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(port);
  if (bind(listenfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
    perror("bind");
    return 1;
  }

  // Listen for connections
  if (listen(listenfd, 10) == -1) {
    perror("listen");
    return 1;
  }
  printf("Listening on port %d...\n", port);

// Open log file in append mode with forced flushing
  log_file = fopen("decoy_connections.log", "a+");
  if (log_file == NULL) {
    perror("fopen");
    return 1;
  }
  setvbuf(log_file, NULL, _IOLBF, 0); // Set line buffering for immediate flush

  // Accept connections and log information
  while (1) {
    client_addr_len = sizeof(client_addr);
    connfd = accept(listenfd, (struct sockaddr*)&client_addr, &client_addr_len);
    if (connfd == -1) {
      perror("accept");
      continue;
    }

    // Get client IP address
    inet_ntop(AF_INET, &(client_addr.sin_addr), ip_address, sizeof(ip_address));

    // Get current time
    current_time = time(NULL);
    time_info = localtime(&current_time);

    // Log information
    fprintf(log_file, "%04d-%02d-%02d %02d:%02d:%02d, %s, %d\n",
            time_info->tm_year + 1900, time_info->tm_mon + 1, time_info->tm_mday,
            time_info->tm_hour, time_info->tm_min, time_info->tm_sec, ip_address,
	    port);

    // Flush the log file to ensure immediate write
    fflush(log_file);

    // Close connection
    close(connfd);
  }

  // Close log file and socket
  fclose(log_file);
  close(listenfd);

  return 0;
}
