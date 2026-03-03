Page({
  data: {
    parentId: null,
    parent: {
      nickname: '',
      phones: [''],
      remark: ''
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
            phones: [''],
            remark: ''
          }
        });
      }
    });
  },

  // 输入家长姓名
  inputNickname: function(e) {
    this.setData({
      'parent.nickname': e.detail.value
    });
  },

  // 输入手机号
  inputPhone: function(e) {
    const index = e.currentTarget.dataset.index;
    const phones = [...this.data.parent.phones];
    phones[index] = e.detail.value;
    this.setData({
      'parent.phones': phones
    });
  },

  // 添加手机号
  addPhone: function() {
    const phones = [...this.data.parent.phones];
    phones.push('');
    this.setData({
      'parent.phones': phones
    });
  },

  // 删除手机号
  deletePhone: function(e) {
    const index = e.currentTarget.dataset.index;
    if (this.data.parent.phones.length > 1) {
      const phones = [...this.data.parent.phones];
      phones.splice(index, 1);
      this.setData({
        'parent.phones': phones
      });
    }
  },

  // 输入备注
  inputRemark: function(e) {
    this.setData({
      'parent.remark': e.detail.value
    });
  },

  // 保存家长信息
  saveParent: function() {
    const { parentId, parent } = this.data;
    
    if (!parent.nickname) {
      wx.showToast({
        title: '请输入家长姓名',
        icon: 'none'
      });
      return;
    }

    const app = getApp();
    const url = parentId ? '/school/parents/' + parentId : '/school/parents';
    const method = parentId ? 'PUT' : 'POST';
    
    app.request(url, method, parent, res => {
      if (res.code === 200) {
        wx.showToast({
          title: parentId ? '更新成功' : '添加成功',
          icon: 'none'
        });
        wx.navigateBack();
      }
    });
  }
});