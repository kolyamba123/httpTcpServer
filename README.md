# httpTcpServer
Simple http server for resending message over TCP

Use POST request with headers X-TCP-Host (TCP server host) and X-TCP-Port (TCP server port) and message in body. Add header "Content-Type:application/xml" if request body is XML.
