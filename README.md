# checkmk-agent-plugin-yum

Checks for updates on RPM-based distributions via yum.

Inspired by https://github.com/lgbff/lgb_check_mk_plugins/tree/master/aptng.

See [https://docs.checkmk.com/latest/de/mkps.html#H1:Installation,%20Update%20and%20Removal](https://docs.checkmk.com/latest/de/mkps.html#H1:Installation,%20Update%20and%20Removal) for details on Check_MK package management.

Now built by GitHub Actions.


## 🛠️ Development

A local Checkmk with the check plugin integrated can be run via `docker-compose.yml`. Connect to it via browsing to
URL [http://localhost:5000/cmk/check_mk/index.py](http://localhost:5000/cmk/check_mk/index.py)

This setup comes with a preconfigured site `cmk` and user `cmkadmin` with password `cmkadmin`. Aside the **checkmk**
container a **client** container is running, which can be used for testing.

### 📃 Logging of bakery jobs

When debugging inside the container **checkmk**: `tail -f /omd/sites/cmk//var/log/ui-job-scheduler/*`
