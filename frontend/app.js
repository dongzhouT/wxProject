App({
  globalData: {
    userInfo: null,
    token: '',
    role: '', // 'admin', 'school', 'parent'
    baseUrl: 'http://127.0.0.1:5001/api' // 本地服务器地址
  },
  
  onLaunch: function() {
    // 从本地存储获取token和用户信息
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    const role = wx.getStorageSync('role');
    
    if (token && userInfo && role) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
      this.globalData.role = role;
    } else {
      // 跳转到登录页
      wx.redirectTo({
        url: '/pages/common/login/login'
      });
    }
  },
  
  // 登录方法
  login: function(role, userInfo, token) {
    this.globalData.role = role;
    this.globalData.userInfo = userInfo;
    this.globalData.token = token;
    
    // 存储到本地
    wx.setStorageSync('role', role);
    wx.setStorageSync('userInfo', userInfo);
    wx.setStorageSync('token', token);
    
    // 根据角色跳转到对应首页
    let homePage = '';
    wx.showToast({
      title: `登录role ${role}`,
      icon: 'none'
    });
    switch(role) {
      case 'admin':
        homePage = '/pages/admin/index/index';
        break;
      case 'school':
        homePage = '/pages/school/index/index';
        break;
      case 'parent':
        homePage = '/pages/parent/index/index';
        break;
      default:
        homePage = '/pages/common/login/login';
    }
    
    // 根据页面类型选择跳转方式
    if (homePage === '/pages/parent/index/index' || homePage === '/pages/common/login/login') {
      // 对于tabBar页面，使用switchTab
      wx.switchTab({
        url: homePage
      });
    } else {
      // 对于非tabBar页面，使用redirectTo
      wx.redirectTo({
        url: homePage
      });
    }
  },
  
  // 登出方法
  logout: function() {
    this.globalData.role = '';
    this.globalData.userInfo = null;
    this.globalData.token = '';
    
    // 清除本地存储
    wx.removeStorageSync('role');
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('token');
    
    // 跳转到登录页
    wx.redirectTo({
      url: '/pages/common/login/login'
    });
  },
  
  // 发送请求的方法
  request: function(url, method, data, success, fail) {
    const token = this.globalData.token;
    
    wx.request({
      url: this.globalData.baseUrl + url,
      method: method,
      data: data,
      header: {
        'content-type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: res => {
        if (res.statusCode === 401) {
          // Token过期或无效，跳转到登录页
          wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          });
          this.logout();
        } else {
          success && success(res.data);
        }
      },
      fail: err => {
        fail && fail(err);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  }
});