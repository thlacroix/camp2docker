var http = require('http');

http.createServer(function(req, res){
	res.end('Hello World');
}).listen(process.env.PORT);
