Page({
  data: {
    parentId: null,
    parent: {
      nickname: '',
      phones: [],
      remark: '',
      orders: []
    }
  },

  onLoad: function(options) {
    if (options.parentId) {
      this.setData({
        parentId: options.parentId
      });
      this.loadParentDetail();
    }
  },

  // 加载家长详情
  loadParentDetail: function() {
    const app = getApp();
    app.request('/school/parents/' + this.data.parentId, 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          parent: res.data || {
            nickname: '',
            phones: [],
            remark: '',
            orders: []
          }
        });
      }
    });
  },

  // 编辑家长信息
  editParent: function() {
    wx.navigateTo({
      url: '/pages/school/parents/edit?parentId=' + this.data.parentId
    });
  },

  // 添加订单
  addOrder: function() {
    wx.navigateTo({
      url: '/pages/school/orders/edit?parentId=' + this.data.parentId
    });
  }
});