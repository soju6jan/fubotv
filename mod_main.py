from tool import ToolUtil

from .fubotv_handle import Fubotv
from .setup import *


class ModuleMain(PluginModuleBase):
    db_default = {
        f'db_version' : '1',
        f'token_refresh_hour' : '5',
        f'token_time' : '',
        f'token' : '',
        f'email': '',
        f'password': '',
    }

    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name='main', first_menu='list')
        self.ch_list = None


    def process_menu(self, page_name, req):
        arg = P.ModelSetting.to_dict()
        arg['api_m3u'] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/m3u")
        return render_template(f'{P.package_name}_{self.name}_{page_name}.html', arg=arg)
    
    
    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'login_check':
            data = self.token_refresh(force=True)
            ret = {'ret':'success', 'json':data}
        elif command == 'broad_list':
            ret = {'ret':'success', 'ch_list':Fubotv.ch_list()}
        elif command == 'play_url':
            url = Fubotv.get_url(P.ModelSetting.get('token'), arg1)
            ret = {'ret':'success', 'data':url}
        return jsonify(ret)


    def process_api(self, sub, req):
        try:
            if sub == 'm3u':
                return self.make_m3u()
            elif sub == 'url.m3u8':
                url = Fubotv.get_url(P.ModelSetting.get('token'), req.args.get('ch_id'))
                return redirect(url, code=302)
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())
        
    ################################################################
    
    def make_m3u(self):
        M3U_FORMAT = '#EXTINF:-1 tvg-id=\"{id}\" tvg-name=\"{title}\" tvg-logo=\"{logo}\" group-title=\"{group}\" tvg-chno=\"{ch_no}\" tvh-chnum=\"{ch_no}\",{title}\n{url}\n' 
        m3u = '#EXTM3U\n'
        for idx, item in enumerate(Fubotv.ch_list()):
            m3u += M3U_FORMAT.format(
                id=item['id'],
                title=item['name'],
                group="fubotv",
                ch_no=str(idx+1),
                url=ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={item['id']}"),
                logo= item['logo'],
            )
        return m3u


    def token_refresh(self, force=False):
        flag = False
        form = '%Y-%m-%d %H:%M:%S'
        if force:
            flag = True
        if flag == False and P.ModelSetting.get('token') == '':
            flag = True
        if flag == False:
            last_time_str = P.ModelSetting.get('token_time')
            if last_time_str == '':
                flag = True
            else:
                last_time = datetime.strptime(last_time_str, form)
                if last_time + timedelta(hours=P.ModelSetting.get_int('token_refresh_hour')) < datetime.now():
                    flag = True 
        if flag:
            data = Fubotv.login(P.ModelSetting.get('email'), P.ModelSetting.get('password'))
            if 'access_token' in data:
                P.ModelSetting.set('token', data['access_token'])
                P.ModelSetting.set('token_time', datetime.now().strftime(form))
            return data
        return P.ModelSetting.get('token')

