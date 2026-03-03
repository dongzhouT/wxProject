Page({
  data: {
    schoolId: '',
    schoolName: '',
    accountLimit: 3,
    accounts: [],
    searchText: '',
    showAddModal: false,
    showEditModal: false,
    showDeleteModal: false,
    deleteAccountId: null,
    roles: ['admin', 'staff'],
    newAccount: {
      wechat_name: '',
      real_name: '',
      phone: '',
      role: 'staff',
      roleIndex: 1
    },
    editAccount: {
      id: '',
      wechat_name: '',
      real_name: '',
      phone: '',
      role: 'staff',
      roleIndex: 1
    }
  },

  onLoad: function(options) {
    this.setData({
      schoolId: options.schoolId,
      schoolName: options.schoolName,
      accountLimit: parseInt(options.limit) || 3
    });
    this.getAccounts();
  },

  onShow: function() {
    this.getAccounts();
  },

  // 获取学校账户列表
  getAccounts: function() {
    const app = getApp();
    app.request('/admin/accounts', 'GET', null, 
      (res) => {
        if (res.code === 200) {
          // 筛选当前学校的账户
          const schoolAccounts = res.data.filter(account => account.school_id == this.data.schoolId);
          this.setData({
            accounts: schoolAccounts
          });
        } else {
          wx.showToast({
            title: res.message || '获取账户列表失败',
            icon: 'none'
          });
        }
      },
      (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    );
  },

  // 搜索账户
  searchAccounts: function() {
    const searchText = this.data.searchText;
    const accounts = this.data.accounts;
    
    if (!searchText) {
      this.getAccounts();
      return;
    }
    
    const filteredAccounts = accounts.filter(account => 
      account.username.includes(searchText) || 
      account.real_name.includes(searchText) || 
      account.phone.includes(searchText)
    );
    
    this.setData({
      accounts: filteredAccounts
    });
  },

  // 输入搜索文本
  inputSearch: function(e) {
    this.setData({
      searchText: e.detail.value
    });
  },

  // 显示添加账户模态框
  showAddAccountModal: function() {
    // 检查账户数量是否达到上限
    if (this.data.accounts.length >= this.data.accountLimit) {
      wx.showToast({
        title: '账户数量已达到上限',
        icon: 'none'
      });
      return;
    }
    
    this.setData({
      showAddModal: true,
      newAccount: {
        wechat_name: '',
        real_name: '',
        phone: '',
        role: 'staff',
        roleIndex: 1
      }
    });
  },

  // 隐藏添加账户模态框
  hideAddAccountModal: function() {
    this.setData({
      showAddModal: false
    });
  },

  // 输入微信名称
  inputWechatName: function(e) {
    this.setData({
      'newAccount.wechat_name': e.detail.value
    });
  },

  // 输入真实姓名
  inputRealName: function(e) {
    this.setData({
      'newAccount.real_name': e.detail.value
    });
  },

  // 输入电话
  inputPhone: function(e) {
    this.setData({
      'newAccount.phone': e.detail.value
    });
  },

  // 角色选择
  bindRoleChange: function(e) {
    const roleIndex = e.detail.value;
    const role = this.data.roles[roleIndex];
    this.setData({
      'newAccount.roleIndex': roleIndex,
      'newAccount.role': role
    });
  },

  // 添加账户
  addAccount: function() {
    const newAccount = this.data.newAccount;
    
    // 验证必填字段
    if (!newAccount.wechat_name || !newAccount.real_name || !newAccount.phone) {
      wx.showToast({
        title: '请填写必填字段',
        icon: 'none'
      });
      return;
    }
    
    // 添加学校ID，使用微信名称作为用户名
    const accountData = {
      ...newAccount,
      school_id: this.data.schoolId,
      username: newAccount.wechat_name // 保留用户名字段以保持兼容性
    };
    delete accountData.roleIndex;
    
    const app = getApp();
    app.request('/admin/accounts', 'POST', accountData, 
      (res) => {
        if (res.code === 201) {
          wx.showToast({
            title: '账户创建成功',
            icon: 'success'
          });
          this.hideAddAccountModal();
          this.getAccounts();
        } else {
          wx.showToast({
            title: res.message || '创建账户失败',
            icon: 'none'
          });
        }
      },
      (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    );
  },

  // 显示编辑账户模态框
  showEditAccountModal: function(e) {
    const account = e.currentTarget.dataset.account;
    const roleIndex = this.data.roles.indexOf(account.role);
    this.setData({
      showEditModal: true,
      editAccount: {
        id: account.id,
        wechat_name: account.wechat_name || account.username,
        real_name: account.real_name,
        phone: account.phone,
        role: account.role,
        roleIndex: roleIndex
      }
    });
  },

  // 隐藏编辑账户模态框
  hideEditAccountModal: function() {
    this.setData({
      showEditModal: false
    });
  },

  // 输入编辑微信名称
  inputEditWechatName: function(e) {
    this.setData({
      'editAccount.wechat_name': e.detail.value
    });
  },

  // 输入编辑真实姓名
  inputEditRealName: function(e) {
    this.setData({
      'editAccount.real_name': e.detail.value
    });
  },

  // 输入编辑电话
  inputEditPhone: function(e) {
    this.setData({
      'editAccount.phone': e.detail.value
    });
  },

  // 编辑角色选择
  bindEditRoleChange: function(e) {
    const roleIndex = e.detail.value;
    const role = this.data.roles[roleIndex];
    this.setData({
      'editAccount.roleIndex': roleIndex,
      'editAccount.role': role
    });
  },

  // 更新账户
  updateAccount: function() {
    const editAccount = this.data.editAccount;
    
    // 验证必填字段
    if (!editAccount.wechat_name || !editAccount.real_name || !editAccount.phone) {
      wx.showToast({
        title: '请填写必填字段',
        icon: 'none'
      });
      return;
    }
    
    // 准备更新数据
    const accountData = {
      ...editAccount,
      username: editAccount.wechat_name // 保留用户名字段以保持兼容性
    };
    delete accountData.id;
    delete accountData.roleIndex;
    
    const app = getApp();
    app.request(`/admin/accounts/${editAccount.id}`, 'PUT', accountData, 
      (res) => {
        if (res.code === 200) {
          wx.showToast({
            title: '账户信息更新成功',
            icon: 'success'
          });
          this.hideEditAccountModal();
          this.getAccounts();
        } else {
          wx.showToast({
            title: res.message || '更新账户失败',
            icon: 'none'
          });
        }
      },
      (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    );
  },

  // 确认删除账户
  confirmDeleteAccount: function(e) {
    const accountId = e.currentTarget.dataset.id;
    this.setData({
      showDeleteModal: true,
      deleteAccountId: accountId
    });
  },

  // 隐藏删除模态框
  hideDeleteModal: function() {
    this.setData({
      showDeleteModal: false,
      deleteAccountId: null
    });
  },

  // 删除账户
  deleteAccount: function() {
    const accountId = this.data.deleteAccountId;
    
    const app = getApp();
    app.request(`/admin/accounts/${accountId}`, 'DELETE', null, 
      (res) => {
        if (res.code === 200) {
          wx.showToast({
            title: '账户删除成功',
            icon: 'success'
          });
          this.hideDeleteModal();
          this.getAccounts();
        } else {
          wx.showToast({
            title: res.message || '删除账户失败',
            icon: 'none'
          });
        }
      },
      (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    );
  }
});
