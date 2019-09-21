# 开发者接入Mixin Network说明

[1创建mixin账户](https://github.com/myrual/mixin_dev_resource/blob/master/mixin_network_intro_for_dev.md#1-开发者自己创建一个mixin-账户)

[2配置机器人](https://github.com/myrual/mixin_dev_resource/blob/master/mixin_network_intro_for_dev.md#2-开发者使用注册的mixin账户创建App并进行配置)

[3接入mixin网络](https://github.com/myrual/mixin_dev_resource/blob/master/mixin_network_intro_for_dev.md#3-编程接入mixin网络)


## 1. 开发者自己创建一个mixin 账户

https://mixin.one 


## 2. 开发者使用注册的mixin账户创建App并进行配置

访问 https://developers.mixin.one/dashboard ， 使用Mixin App的摄像头扫描二维码登陆。

填写注册App需要的信息，包括callback URL，目前图标暂时不是必选的。Url和callback url也可以随便先填着。注册成功 App 之后，你就拥有了一个mixinapp里面的一个机器人账户，它的Mixin ID是7000开头的那一段数字。通过Mixin ID在Mixin Messenger里面查找加到通讯录之后就可以把它加到你自己创建的群里面。

回到开发者界面，你可以进行以下操作产生相关信息，在整合App和Mixin的时候需要用到。

  1. 点击相应 APP 的 “Click to generate a new secret”， 会产生一个字符串，这个serect在下面获取access token中可以选择使用。
  
  2. 点击相应 App 的 “Click to generate a new session”，会出现三组数据和一个私钥：请牢记在心，因为私钥部分不会再显示一次。
  
      1. 第一行的 6 位数字是 api接入 的提现/转账PIN 码，此处也是机器人的提现/转账密码
      
      2. 第二行的 UUID 是 session ID，
      
      3. 第三行是PIN_TOKEN， 
      
      4. 最后一部分 RSA PRIVATE KEY 是跟 API 进行交互时用来签名 JWT 的私钥。

注意每次产生一个新的secret和session的相关信息之后，之前产生的secret和session相关信息都会失效。

## 3. 编程接入mixin网络

xin网络本身是一个公链，mixin app是这个公链开发团队维护的一个App。

因此使用xin公链有两种方式：

一种是获取mixin app的用户，通过mixin app 来完成转账和提现。

另一种是自己创建用户，管理用户数据库，仅仅通过mixin公链转账和支付。

接入mixin网络，需要使用JWT RSA token，并将 http header里面的字段设定为 Authorization: Bearer ACCESS_TOKEN

ACCESS_TOKEN 生成方式如下
```
API 认证方式为标准的 JWT RSA 签名，JWT claims 必须包含的信息为

		"uid": 注册的 App 的 ID(UUID 格式那个，不是7000开头的),
		"sid": 上一部分获取的 session ID,
		"iat": 签名时间，时间必须跟 Mixin 服务器时间基本一致,
		"exp": 过期时间，建议不要设置太长，3 分钟足够,
		"jti": 请求的唯一 ID，必须使用标准的 UUID 格式,
		"sig": sha256(method+URI+body),  // ( "POST" + "/Transfer" + "{"key":value})
```


### 3.1 获取某个Mixin app的用户

引导用户访问下面的网址，用户通过Mixin App摄像头扫码就可以登陆
```
https://mixin.one/oauth/authorize?client_id=CLIENT_ID&scope=SCOPE&code_challenge=PKCE
```
其中 CLIENT_ID是 dashboard里面显示的 UUID格式的那串文字

SCOPE可以是如下组合
```
PROFILE:READ
PROFILE:READ+PHONE:READ
PROFILE:READ+ASSETS:READ
PROFILE:READ+PHONE:READ+ASSETS:READ
```
以下是例子
```
https://mixin.one/oauth/authorize?client_id=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&scope=PROFILE:READ
https://mixin.one/oauth/authorize?client_id=3c5fd587-5ac3-4fb6-b294-423ba3473f7d&scope=PROFILE:READ+ASSETS:READ
```

一旦用户使用Mixin app摄像头扫描二维码之后，mixin服务器会引导用户的浏览器访问在dashboard里面设置的callback URL
并且带有参数
```
{'code': u'a83f4424a205c36d9086ff751c2efc282766c92a3fb40aa1b26546b4187f95ba'}
```
使用这个参数访问 https://api.mixin.one/oauth/token 
```
POST https://api.mixin.one/oauth/token
{
  "client_id": "CLIENT_ID",
  "code": "authorization code from step above",
  "client_secret": "optional client secret",
  "code_verifier": "optional PKCE code verifier"
}
```
会获得结果
```
{u'data': {u'access_token': u'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJhaWQiOiI5NmMyNGI4Mi01MjY2LTQ5YWQtYjc4NS03MWZhYjE4Y2FiYTEiLCJleHAiOjE1NTU4NTc4MjEsImlhdCI6MTUyNDMyMTgyMSwiaXNzIjoiM2M1ZmQ1ODctNWFjMy00ZmI2LWIyOTQtNDIzYmEzNDczZjdkIn0.Hv78yzF40GeKxw4J0tIahd1tvYdlrmJw0YMZf8OTCZBclyr3Bi-nIAEZWnOej9YuQ3elyajI6UPBQdW22i4DHrSyDNt3i2d8YXfrOJ_F1h7Raq7whoLkVr2vAFuch-ZvVBEtTyv8RDkU8-36f4pgzdMSheb3gEQDtM1d904mNIc', u'scope': u'PROFILE:READ ASSETS:READ'}}
```
这个access token是后面一些操作需要设置在http header里面的


```
"""python code"""
personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})
```
使用上面的参数里面的数据可以访问到客户的一些基本信息

```
GET -H "Authorization: Bearer ACCESS_TOKEN" https://api.mixin.one/me

=>

{
  "data": {
    "type": "user",
    "user_id": "773e5e77-4107-45c2-b648-8fc722ed77f5",
    "name": "Team Mixin",
    "identity_number": "7000"
  }
}
```


### 3.2 获取mixin app用户的资产列表
```
GET -H "Authorization: Bearer ACCESS_TOKEN" https://api.mixin.one/assets

=>

{
  "data": {
    "type": "user",
    "user_id": "773e5e77-4107-45c2-b648-8fc722ed77f5",
    "name": "Team Mixin",
    "identity_number": "7000"
  }
}
```
        personinfo = requests.get('https://api.mixin.one/me', headers = {"Authorization":"Bearer " + access_token})

### 3.3 获取mixin app用户的某个资产余额
```
GET -H "Authorization: Bearer ACCESS_TOKEN" https://api.mixin.one/assets/asset-uuid

=>

{
  "data": {
    "type": "user",
    "user_id": "773e5e77-4107-45c2-b648-8fc722ed77f5",
    "name": "Team Mixin",
    "identity_number": "7000"
  }
}
```

#### 3.1.1 使用自己的机器人转账给用户
注意：ACCESS_TOKEN 需要使用JWT token，而且trace_id不能是使用过的
```
curl -X POST -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/transfers

{ "asset_id": "", // 默认值是空 "counter_user_id": UUID, // 主播的 "amount": "amount", "pin": "encrypted_pin", // 加密的 pin "trace_id": UUID, // 可以随时用这个 id 来查询转帐的记录 "memo": "备注", }

=>

{ "type": "transfer", "snapshot_id": UUID, "trace_id": UUID, ... }
```

#### 在post请求中使用的加密的pin的获取方法

在开发者dashboard中获得的pin_token 是一个经过base64 编码字符串，并且经过了公钥加密，


我们需要首先对PIN_TOKEN 以base64进行解码，然后用获取的私钥对字符进行RSA512解密，获得AES加密需要的key，暂时称为AES_KEY

RSA512的具体算法是 PKCS1 OAEP，hash算法是sha256，label是dashboard 里面的sessionid，

然后组织待加密的内容：

pin + timestamp + 计数器

pin是从dashboard获取的短数字，假设是123456

timestamp是 unix的utc时间戳，类似1524723524，用hex表示就是 0x5AE16F44, 8字节，64位。低字节在前，高字节在后。

计数器是一个本地存储整型数，类似12, 8字节，64位，低字节在前，高字节在后，每次上发的计数器必须比上一次大，无论发送成功还是失败。

将整个内容看成一个数组，或者byte array，或者字符串都可以

那么整个内容就是 0x363534333231 + 0x446FE15A00000000 + 0x0100000000000000

得到内容之后，如果内容长度不是16的整数倍，需要在尾部补齐一些数据为16的整数倍。

具体的补齐内容是需要补齐的字节的数量。比如需要补齐10个字节才能满足16的整数倍，那么需要补齐10个0x0a，10个10

将补齐后的数据使用AES加密算法，使用AES_KEY作为密钥进行加密。

然后使用随机数生成器生成一个16字节的随机数组称为 iv，然后把加密后的结果追加在随机数组后面。

然后把整个iv+加密结果进行base64编码，作为上传参数的里面的pin的值


#### 3.1.2 引导用户给别的用户转账

### 3.2 收取相关的消息

mixin服务器会给机器人一系列消息回执，包括但不限于

机器人给其他用户付款后的流水，别人给机器付款的消息，用户给机器人发的消息

机器人在收取到消息之后，需要向服务器发送消息接受成功的回执，mixin客户端才会显示消息已经送达。

#### 3.2.1 接收消息流程

1. 创建websocket客户端，然后连接到服务器上
2. 发送开始监听网络命令
3. 服务器开始推送各种消息
4. 处理消息并且与服务器交互

##### websocket参数配置

websocket参数分别是
根目录是 wss://blaze.mixin.one/

发送接收格式是binary

自定义http header 参数 ["Authorization:Bearer " + ACCESS_TOKEN]，这个ACCESS_TOKEN就是标准的JWT_TOKEN，与付款API使用的算法相同。

同时需要支持subprotocol "Mixin-Blaze-1"

```
    ws = websocket.WebSocketApp("wss://blaze.mixin.one/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              header = ["Authorization:Bearer " + encoded],
                              subprotocols = ["Mixin-Blaze-1"],
                              on_data = on_data)
```

通过websocket发送的所有数据都是经过gzip压缩的，此处的gzip 压缩是将要发送的内容压缩成gzip文件格式然后发送。仅仅将内容通过zlib库压缩是不行的。

##### 可以发送给服务器的指令和格式
```
完整格式 {"id":"uuid-value-xxxx","action":"yyyy", "parameter":"zzz", "data":"000111222", "error":"404"}

如果不需要参数，那么直接key也不要写

{"id":"uuid-value-xxxx","action":"yyyy"}
```
id必须是uuid格式。


### 3.2 自己拥有用户，仅仅使用mixin网络来转账

这种使用场景需要使用标准的JWT RSA token，
此后对所有的 API 访问包含上面签名过的 JWT token 做为一个 Bearer Authorization HTTP header。

#### 3.2.1 通过上面 APP 的 JWT RSA （ACCESS_TOKEN）签名， 创建用户(主播或者土豪)

*注意：这里是 APP 的 ACCESS_TOKEN *

每个用户都是由一个标准的 RSA 密钥代表的，首先需要在本地生成一对 RSA 的密钥，并保存好 PRIVATE KEY，然后将 PUBLIC KEY 以 Base64 Encode 的形式做为相应参数（session_secret）发送给 Mixin 服务器节点，同时可选的发送一个用户名字来方便区分用户。

curl -X POST -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/users

{
  "session_secret":  Base64 of RSA PUBLIC KEY,
  "full_name":       可选的用来方便区分用户的名字,
}

=>

{
  "data": {
    "type":        "user",
    "user_id":     UUID,
    "session_id":  UUID,
    "pin_token":   RSA PRIVATE KEY,
    ...
  }
}

#### 3.2.2 为主播或土豪准备转帐需要的 PIN (支付密码)

每个 Mixin 的用户都需要有一个 PIN 码，转帐要用。创建新用户的时候是不包含这个密码的，所以需要更新。

*注意：这里的 ACCESS_TOKEN 跟 1 中的加密方式一致，但是是用 2 中用户的信息（相当于对每个独立的用户进行的操作）*

curl -X POXT -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/pin/update 

{
"old_pin": "", // 默认值是空
"pin": "encrypted_pin", // 加密的 pin
}



将整个内容看成一个数组，或者byte array，或者字符串都可
用key对内容用AES加密算法加密。
如何得到加密的 PIN
1. 服务器返回的 pin_token 解密，得到 key
2. 得到一个 pin + LittleEndian(time) + iterator (每次加密都要加 1)
3. 进行 AES 加密

``` golang

func testEncryptPIN(ctx context.Context, pin, pinToken, sessionId string, key *rsa.PrivateKey, iterator uint64) string {
	token, _ := base64.StdEncoding.DecodeString(pinToken)
	keyBytes, err := rsa.DecryptOAEP(sha256.New(), rand.Reader, key, token, []byte(sessionId))
	if err != nil {
		return ""
	}
	pinByte := []byte(pin)
	timeBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(timeBytes, uint64(time.Now().Unix()))
	pinByte = append(pinByte, timeBytes...)
	iteratorBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(iteratorBytes, iterator)
	pinByte = append(pinByte, iteratorBytes...)
	padding := aes.BlockSize - len(pinByte)%aes.BlockSize
	padtext := bytes.Repeat([]byte{byte(padding)}, padding)
	pinByte = append(pinByte, padtext...)
	block, _ := aes.NewCipher(keyBytes)
	ciphertext := make([]byte, aes.BlockSize+len(pinByte))
	iv := ciphertext[:aes.BlockSize]
	io.ReadFull(rand.Reader, iv)
	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext[aes.BlockSize:], pinByte)
	return base64.StdEncoding.EncodeToString(ciphertext)
}

```

#### 4. 用户获取充值地址

每个用户都拥有所有货币 asset 的充值地址，必须通过下面的 API 访问来获取相应 asset 的信息，其中的 public_key 字段为用户的充值地址。

*注意：这里是用户的 ACCESS_TOKEN *

curl -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/assets/UUID

=>

{
  "data": {
    "type":        "asset",
    "asset_id":     UUID,
    "public_key":   Adress,
    ...
  }
}

现在支持的 asset UUID 有两种，BTC 和 ETH，其中 ETH 的地址可以自动支持所有 ERC20 资产的充值。

BTC c6d0c728-2624-429b-8e0d-d9d19b6592fa
ETH 43d61dcd-e413-450d-80b8-101d5e903357

#### 5. 转帐（土豪给主播打赏）

*注意：ACCESS_TOKEN 是土豪的*

curl -X POST -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/transfers

{
"asset_id": "", // 默认值是空
"counter_user_id": UUID, // 主播的
"amount": "amount", 
"pin": "encrypted_pin", // 加密的 pin
"trace_id": UUID, // 可以随时用这个 id 来查询转帐的记录
"memo": "备注", 
}


=> 

{
    "type":        "transfer",
    "snapshot_id":     UUID,
    "trace_id": UUID,
    ...
}

## 6. 添加提现地址

*注意： ACCESS_TOKEN 属于用户*

curl -X POST -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/addresses

{
"asset_id" : UUID,
"public_key": "ETH OR BTC",
"label": "备注"，
"pin": "encrypted_pin", // 加密的 pin
}

=>

{
    "type":        "address",
    "address_id":     UUID,
    "asset_id": UUID,
    "public_key": "ETH OR BTC",
    ...
}

## 7. 提现

*注意： ACCESS_TOKEN 属于用户*

curl -X POST -H "Authorization: Bearer ACCESS_TOKEN" -H "Content-Type: application/json" https://api.mixin.one/withdrawals

{
"address_id": UUID, // 提现的地址
"amount": "amount",
"pin": "encrypted_pin", // 加密的 pin
"trace_id": UUID, // 可以随时用这个 id 来查询转帐的记录
"memo": "备注", 
}

=> 

{
    "type":        "withdrawal",
    "snapshot_id":     UUID,
    "trace_id": UUID,
    ...
}
