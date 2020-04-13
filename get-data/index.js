console.log('Loading event');
var aws = require('aws-sdk');
var s3 = new aws.S3({apiVersion: '2006-03-01'});
var https = require ('https');

exports.handler = function(event, context) {
    var bucket = 'BUCKET_NAME';
    var key = 'FILE_NAME';
    var body = '';
    var url = "URL_NAME"
    
    https.get(url, function(res) {
        console.log("Response: " + res.statusCode);
        res.on("data", function(chunk) {
            console.log('chunk: ');
            res.setEncoding('utf8');
            body += chunk;
        });

        res.on('end', function(res) {
            console.log('end')
            putObject(context, bucket, key ,body);
        });
    }).on('error', function(e) {
        context.done('error', e);
    });

    function putObject(context, bucket, key ,body) {
        var params = {Bucket: bucket, Key: key, Body: body};
        console.log('s3 putObject' + params);
        
        s3.putObject(params, function(err, data) {
            if (err) {
                console.log('put error' + err);  
                context.done(null, err);
            } else {
                console.log("Successfully uploaded data to myBucket/myKey");
                context.done(null, "done");
            }
        });
    }
};
