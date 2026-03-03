Page({
  data: {
    role: 'parent', // 默认选择家长角色
    username: 'admin',
    password: 'admin123',
    loading: false
  },
  
  // 切换角色
  switchRole: function(e) {
    this.setData({
      role: e.currentTarget.dataset.role
    });
  },
  
  // 输入用户名
  inputUsername: function(e) {
    this.setData({
      username: e.detail.value
    });
  },
  
  // 输入密码
  inputPassword: function(e) {
    this.setData({
      password: e.detail.value
    });
  },
  
  // 登录
  login: function() {
    const { role, username, password } = this.data;
    
    if (role === 'parent' || role === 'school') {
      // 家长和学校登录都使用微信登录
      this.wechatLogin();
    } else {
      // 管理员使用账号密码登录
      if (!username || !password) {
        wx.showToast({
          title: '请输入用户名和密码',
          icon: 'none'
        });
        return;
      }
      
      this.accountLogin(role, username, password);
    }
  },
  
  // 微信登录
  wechatLogin: function() {
    const that = this;
    that.setData({ loading: true });
    const app = getApp();
    const { role } = that.data;
    
    if (role === 'school') {
      // 学校登录：模拟获取微信手机号并登录
      // 实际项目中，这里应该使用button的open-type="getPhoneNumber"获取手机号
      // 然后调用后端接口进行登录
      
      // 模拟手机号（实际项目中应该是从微信获取的真实手机号）
      const mockPhone = '13800138000';
      
      wx.request({
        url: app.globalData.baseUrl + '/school/login',
        method: 'POST',
        data: {
          phone: mockPhone
        },
        success: result => {
          that.setData({ loading: false });
          
          if (result.statusCode === 200) {
            wx.showToast({
              title: '登录成功',
              icon: 'none'
            });
            // 登录成功
            const app = getApp();
            app.login('school', result.data.data.userInfo, result.data.data.token);
          } else {
            wx.showToast({
              title: result.data.message || '登录失败',
              icon: 'none'
            });
          }
        },
        fail: err => {
          that.setData({ loading: false });
          wx.showToast({
            title: '网络请求失败',
            icon: 'none'
          });
        }
      });
    } else {
      // 家长登录：使用微信登录code
      wx.login({
        success: res => {
          if (res.code) {
            // 发送code到服务器获取openid和session_key
            wx.request({
              url: app.globalData.baseUrl + '/parent/login',
              method: 'POST',
              data: {
                code: res.code
              },
              success: result => {
                console.info('------');
                that.setData({ loading: false });
                
                if (result.statusCode === 200) {
                  console.info('login sucess');
                  console.log(result);
                  // 登录成功
                  const app = getApp();
                  app.login('parent', result.data.parent, result.data.access_token);
                } else {
                  wx.showToast({
                    title: result.data.message || '登录失败',
                    icon: 'none'
                  });
                }
              },
              fail: err => {
                that.setData({ loading: false });
                wx.showToast({
                  title: '网络请求失败',
                  icon: 'none'
                });
              }
            });
          } else {
            that.setData({ loading: false });
            wx.showToast({
              title: '获取登录凭证失败',
              icon: 'none'
            });
          }
        },
        fail: err => {
          that.setData({ loading: false });
          wx.showToast({
            title: '微信登录失败',
            icon: 'none'
          });
        }
      });
    }
  },
  


  // 账号密码登录
  accountLogin: function(role, username, password) {
    const that = this;
    that.setData({ loading: true });
    const app = getApp();
    
    // 构建请求URL
    const url = role === 'admin' ? '/admin/login' : '/school/login';
    
    // 发送登录请求
    wx.request({
      url: app.globalData.baseUrl + url,
      method: 'POST',
      data: {
        username: username,
        password: password
      },
      success: res => {
        that.setData({ loading: false });
        
        if (res.statusCode === 200) {
          wx.showToast({
            title: '登录成功',
            icon: 'none'
          });
          // 登录成功
          const app = getApp();
          app.login(role, res.data.admin || res.data.account, res.data.access_token);
        } else {
          wx.showToast({
            title: res.data.message || '登录失败',
            icon: 'none'
          });
        }
      },
      fail: err => {
        that.setData({ loading: false });
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  }
});