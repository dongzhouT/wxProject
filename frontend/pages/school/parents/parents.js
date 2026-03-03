Page({
  data: {
    parents: [],
    searchText: ''
  },

  onLoad: function() {
    this.loadParents();
  },

  onShow: function() {
    this.loadParents();
  },

  // 加载家长数据
  loadParents: function() {
    const app = getApp();
    app.request('/school/parents', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          parents: res.data || []
        });
      }
    });
  },

  // 输入搜索文本
  inputSearch: function(e) {
    this.setData({
      searchText: e.detail.value
    });
  },

  // 搜索家长
  search: function() {
    const app = getApp();
    app.request('/school/parents', 'GET', { search: this.data.searchText }, res => {
      if (res.code === 200) {
        this.setData({
          parents: res.data || []
        });
      }
    });
  },

  // 添加家长
  addParent: function() {
    wx.navigateTo({
      url: '/pages/school/parents/edit'
    });
  },

  // 查看家长详情
  viewDetails: function(e) {
    const parentId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/school/parents/details?parentId=' + parentId
    });
  },

  // 编辑家长信息
  editParent: function(e) {
    const parentId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/school/parents/edit?parentId=' + parentId
    });
  },

  // 删除家长
  deleteParent: function(e) {
    const parentId = e.currentTarget.dataset.id;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这个家长吗？',
      success: res => {
        if (res.confirm) {
          const app = getApp();
          app.request('/school/parents/' + parentId, 'DELETE', {}, res => {
            if (res.code === 200) {
              wx.showToast({
                title: '删除成功',
                icon: 'none'
              });
              this.loadParents();
            }
          });
        }
      }
    });
  }
});