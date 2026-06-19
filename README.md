# Life360 Desktop

A desktop app to view your [Life360](https://www.life360.com/) circles, members
and locations in its own window &mdash; bringing the core experience of the
mobile app to your PC.

> **Prefer the browser version?**
> There is also a browser variant on the
> [`browser` branch](https://github.com/Zeyrox77/Life360-Desktop/tree/browser).

> **Disclaimer**
> This project uses Life360's unofficial API and is **not** affiliated with or
> endorsed by Life360, Inc. Use it only with your own account, at your own risk.
> The API may change or stop working at any time.

---

## Features

- View every circle you belong to and switch between them.
- See each member's avatar, current place/address, battery level, charging
  state and movement status (driving / moving / stationary).
- Live map with all members and saved places.
- Member detail panel: address, coordinates, battery, Wi-Fi, speed, driving
  status, accuracy and last-update time.
- Automatic refresh every 30 seconds, plus a manual refresh button.
- Stays signed in &mdash; your access token is remembered between launches.

## Download & run

### Windows (easiest)

Download `Life360.exe` from the
[Releases page](https://github.com/Zeyrox77/Life360-Desktop/releases),
double-click it, and sign in (see [Signing in](#signing-in) below). No
installation needed.

### Run from source (any OS)

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Zeyrox77/Life360-Desktop.git
cd Life360-Desktop
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python desktop.py
```

## Signing in

Life360 signs most accounts in with a one-time code sent to your email or phone,
so this app signs in with an **access token** copied from a Life360 web session:

1. Open <https://life360.com/login> in a browser and sign in normally
   (email + the code you receive).
2. Press **F12** to open Developer Tools and switch to the **Network** tab.
3. Reload the page (**F5**) and click the request named **`manage-membership`**.
4. Under **Headers -> Request Headers**, scroll to **`Cookie`** and find
   `LIFE360_AUTH_TOKEN=`.
5. Copy everything **after** the `=` up to the next `;`, and paste it into the
   app's token box. (Pasting the whole `LIFE360_AUTH_TOKEN=...;` chunk also
   works &mdash; it is cleaned up automatically.)

Tick **"Keep me signed in on this device"** to stay logged in across restarts.
The token is stored only on your device and never sent to any server. It stays
valid until Life360 expires it; after that, paste a fresh one the same way.

## Troubleshooting

- **"That token was rejected by Life360"** &mdash; the token was copied
  incompletely or has expired. Repeat the steps above and paste a fresh
  `LIFE360_AUTH_TOKEN` value.
- **Blank window on Windows** &mdash; install or repair the
  [Edge WebView2 runtime](https://developer.microsoft.com/microsoft-edge/webview2/)
  (usually already present on Windows 10/11).
- **"Life360 blocked the request"** &mdash; wait a minute, turn off any
  VPN/proxy, and try again.

## License

Released under the [MIT License](LICENSE).
