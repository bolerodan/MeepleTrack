DATABASE = {
    "NAME": 'meeple',
    "USER": 'root',
    "PASS": '',
    "HOST": 'localhost',
    "PORT": '3600'
}

#connectstring = "mysql+mysqldb://%(USER)s:%(PASS)s@%(HOST)s:%(PORT)s/%(NAME)s" % DATABASE
connectstring = 'sqlite:///../meeples.db'


secret_key = '767^&^6767jfdghkjfhgKyi3y98(*&^#($&9387429874'

from datetime import timedelta
session_timeout = timedelta(minutes=60*24)

base_url = 'http://localhost'
BGG_API = 'http://boardgamegeek.com/xmlapi/'

REDIS_SERVER = "localhost"
REDIS_PORT = 6380
REDIS_DB = 0


token_priv = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA4BclcAp86zI46izWPZIgK4AGbbDw2guhjhPyQcmtoAWtuW2K\n1dM3fqq/VGE/9ld+ReCprN4i4t5JVrUfqKFRs18ccGjRydqMkOkvnPDzqp+rh/6o\nZigo4IS4WWIgsFpDpsKWa6BOcf1UCxgRZ68HTcx9T7MKpwhhGH+nwrzUDRVj5ukM\n4SJmxBqxyFZxdj0wTRfeZlHnP5Mp2MrbkVMwuTBRHFifZ8VwpLSigYwCt0/fTorM\nrYp0JNzHTF7YJVSP+Ehup/KQcYa9ACo0zKhAh6KchLlCZ8NBVi00jWQtEwh5ZFsC\n17Ohgfxt8HnIj6kPTn/t2DeTO06ded8BnT1vHQIDAQABAoIBAEIzdFLqNkdBWgEM\nZ+penfRb6QpEyJKR9xNDH0GCNDHfG5h5HRfYQz+/b7Cc3kmHRX2dRmMUaNf+9UmR\nTp4BsmI8SemHfdqVHwu8Z92EbWfNrd4KRHORj6nsa420aJXQxMWiHNAE1sfkIAz6\n+kFYOt8n9ykxaoc3+X9ETyo/oKGQT1oZBHH7P+lR2AQ7du+NypjKdIuYMlydp7aF\nbRvrQ2dh0EE60JN7VLox8XEnUsap1hxma+tdZ8yagYjExvSZPNTInOFOpFXzy+6e\n7p4j3k0XrBstkc9qK7tq2LsfpchAyFcSEOdJI0pzrOQ61h414zoTcCLKJCS5sKig\nj29dVv0CgYEA4Litugwoiv3MZTVs62fKAV6ZAuq91KrbEC54io1nTIu5NYs7ZnMZ\ndw7vRfe7UFQUbINeerh6X0SdP+y2aJqbgsg5Suw8087woiZPhg0uCS6iDQ+6v0QA\nbZWsRjXh9juym4nux0HSboxvW+8LmA76nnvfXuV2gbkU8ekeTLXX0LMCgYEA/0f7\n9FFdG5DCFW9qsQ498p3FkQ2IA6e+/BxdCBNfou3xE5ES1Qr+FWlO5J9iV9clOXU7\nu7n+agdKQBnaPDGxiRT14DvQvejqM4TBnBOvT89KZ7m6k0+bYfOj9JHro1vy/pSr\nQFdFUzo3OcDojweGIgR0LleLmQBALwuc6aLUCO8CgYAgoE+AwoEkZOLHEvGkX+ZB\nOqXGeaRj+wZhHA4eN5d20pZqQrO2FSHuWjm9E9GbQQnSE2SlNqF1sXWPMWPuXfwU\nCdPfn9rY+aOQNzW2hbVYWe/nK5B2cn4JawCfFPWglVxCHs2PGmxd5n/IfjVVt18F\noYB1u6TwApoa4Tin9ILH5wKBgGhwTsf5sZnhc0XJu2CMbxOfMIDThF3aduw1vmnb\nYzkJF6Plqkq2oJSp7Ljj7Bv7zSLgr3tx8H/4U4w+B2aw/e0TQjRmxFOtwoMpQPxV\noVeJeutMtOQnoW5Fe0JHoJvItnUo5ZcBHT+bhZR/M6WwclPgdpevAVGrJJcarSt4\njj7JAoGBAKVAt5feu0h7fo3yrFSkFLtvwnTI2KvT7UwvOxjfZvQt94gy28CUoRq7\n5VFa04F7SVtjlNk8iAw1iCZhbVRc+k/SMukpgy+V7iTq/mZdZI0sw+57RzgWcnoQ\nhCy5NmOb7hhaZRhhkopJYp2cJmprnLujkjNidPB0lGBFJcS9ZWNc\n-----END RSA PRIVATE KEY-----'
token_pub = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4BclcAp86zI46izWPZIg\nK4AGbbDw2guhjhPyQcmtoAWtuW2K1dM3fqq/VGE/9ld+ReCprN4i4t5JVrUfqKFR\ns18ccGjRydqMkOkvnPDzqp+rh/6oZigo4IS4WWIgsFpDpsKWa6BOcf1UCxgRZ68H\nTcx9T7MKpwhhGH+nwrzUDRVj5ukM4SJmxBqxyFZxdj0wTRfeZlHnP5Mp2MrbkVMw\nuTBRHFifZ8VwpLSigYwCt0/fTorMrYp0JNzHTF7YJVSP+Ehup/KQcYa9ACo0zKhA\nh6KchLlCZ8NBVi00jWQtEwh5ZFsC17Ohgfxt8HnIj6kPTn/t2DeTO06ded8BnT1v\nHQIDAQAB\n-----END PUBLIC KEY-----'
