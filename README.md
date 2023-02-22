# chatgpt_plus_proxy_website
Flask反向代理ChatGPT Plus，完美复刻chat.openai.com/chat

## 准备

你应该先登录[ChatGPT Website](https://chat.openai.com/chat)，找到名为`cf_clearance`、`__Secure-next-auth.session-token`、`_puid`的Cookies，复制它们的值。

其中`_puid`为Plus会员专属值，没它不行。

## 安装依赖

``` bash
pip install requests flask
```

## 快速开始

1. 在`chatgpt.py`代码相应位置粘贴`cf_clearance`、`session_token`、`_puid`的值。

2. 运行程序
  ``` bash
  python3 chatgpt_proxy_website.py
  ```

3. 浏览器打开
  ``` plain Text
  http://127.0.0.1:8011/chat
  ```

## 注意事项

1. 只能用于Plus会员账号调用，免费账号会有CF验证。
