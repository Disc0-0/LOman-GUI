// Basic Node.js HTTP server
const http = require('http');

// Configuration
const port = 3000;

// Create HTTP server
const server = http.createServer((req, res) => {
  console.log(`Received request for ${req.url}`);
  
  // Set response headers
  res.writeHead(200, {'Content-Type': 'text/plain'});
  
  // Send response
  res.end('Hello from LOMan server! Press Ctrl+C in the PowerShell window to stop the server.\n');
});

// Start server
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
  console.log('Press Ctrl+C in the PowerShell window to stop the server.');
});

// Handle server shutdown
process.on('SIGINT', () => {
  console.log('SIGINT received - Server shutting down');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

console.log('Node.js server starting...');
