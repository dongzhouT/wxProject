Page({
  data: {
    schools: [],
    searchText: '',
    showAddModal: false,
    showEditModal: false,
    showDeleteModal: false,
    deleteSchoolId: null,
    newSchool: {
      name: '',
      contact_person: '',
      contact_phone: '',
      address: '',
      description: '',
      account_limit: 3
    },
    editSchool: {
      id: '',
      name: '',
      contact_person: '',
      contact_phone: '',
      address: '',
      description: '',
      account_limit: 3
    }
  },

  onLoad: function() {
    this.getSchools();
  },

  onShow: function() {
    this.getSchools();
  },

  // 获取学校列表
  getSchools: function() {
    const app = getApp();
    app.request('/admin/schools', 'GET', null, 
      (res) => {
        if (res.code === 200) {
          this.setData({
            schools: res.data
          });
        } else {
          wx.showToast({
            title: res.message || '获取学校列表失败',
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

  // 搜索学校
  searchSchools: function() {
    const searchText = this.data.searchText;
    const schools = this.data.schools;
    
    if (!searchText) {
      this.getSchools();
      return;
    }
    
    const filteredSchools = schools.filter(school => 
      school.name.includes(searchText) || 
      school.contact_person.includes(searchText) || 
      school.contact_phone.includes(searchText)
    );
    
    this.setData({
      schools: filteredSchools
    });
  },

  // 输入搜索文本
  inputSearch: function(e) {
    this.setData({
      searchText: e.detail.value
    });
  },

  // 显示添加学校模态框
  showAddSchoolModal: function() {
    this.setData({
      showAddModal: true,
      newSchool: {
        name: '',
        contact_person: '',
        contact_phone: '',
        address: '',
        description: ''
      }
    });
  },

  // 隐藏添加学校模态框
  hideAddSchoolModal: function() {
    this.setData({
      showAddModal: false
    });
  },

  // 输入学校名称
  inputSchoolName: function(e) {
    this.setData({
      'newSchool.name': e.detail.value
    });
  },

  // 输入联系人
  inputContactPerson: function(e) {
    this.setData({
      'newSchool.contact_person': e.detail.value
    });
  },

  // 输入联系电话
  inputContactPhone: function(e) {
    this.setData({
      'newSchool.contact_phone': e.detail.value
    });
  },

  // 输入地址
  inputAddress: function(e) {
    this.setData({
      'newSchool.address': e.detail.value
    });
  },

  // 输入描述
  inputDescription: function(e) {
    this.setData({
      'newSchool.description': e.detail.value
    });
  },

  // 输入子账号上限
  inputAccountLimit: function(e) {
    this.setData({
      'newSchool.account_limit': parseInt(e.detail.value) || 3
    });
  },

  // 添加学校
  addSchool: function() {
    const newSchool = this.data.newSchool;
    
    // 验证必填字段
    if (!newSchool.name || !newSchool.contact_person || !newSchool.contact_phone) {
      wx.showToast({
        title: '请填写必填字段',
        icon: 'none'
      });
      return;
    }
    
    const app = getApp();
    app.request('/admin/schools', 'POST', newSchool, 
      (res) => {
        if (res.code === 201) {
          wx.showToast({
            title: '学校创建成功',
            icon: 'success'
          });
          this.hideAddSchoolModal();
          this.getSchools();
        } else {
          wx.showToast({
            title: res.message || '创建学校失败',
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

  // 显示编辑学校模态框
  showEditSchoolModal: function(e) {
    const school = e.currentTarget.dataset.school;
    this.setData({
      showEditModal: true,
      editSchool: {
        id: school.id,
        name: school.name,
        contact_person: school.contact_person,
        contact_phone: school.contact_phone,
        address: school.address || '',
        description: school.description || '',
        account_limit: school.account_limit || 3
      }
    });
  },

  // 隐藏编辑学校模态框
  hideEditSchoolModal: function() {
    this.setData({
      showEditModal: false
    });
  },

  // 输入编辑学校名称
  inputEditSchoolName: function(e) {
    this.setData({
      'editSchool.name': e.detail.value
    });
  },

  // 输入编辑联系人
  inputEditContactPerson: function(e) {
    this.setData({
      'editSchool.contact_person': e.detail.value
    });
  },

  // 输入编辑联系电话
  inputEditContactPhone: function(e) {
    this.setData({
      'editSchool.contact_phone': e.detail.value
    });
  },

  // 输入编辑地址
  inputEditAddress: function(e) {
    this.setData({
      'editSchool.address': e.detail.value
    });
  },

  // 输入编辑描述
  inputEditDescription: function(e) {
    this.setData({
      'editSchool.description': e.detail.value
    });
  },

  // 输入编辑子账号上限
  inputEditAccountLimit: function(e) {
    this.setData({
      'editSchool.account_limit': parseInt(e.detail.value) || 3
    });
  },

  // 更新学校
  updateSchool: function() {
    const editSchool = this.data.editSchool;
    
    // 验证必填字段
    if (!editSchool.name || !editSchool.contact_person || !editSchool.contact_phone) {
      wx.showToast({
        title: '请填写必填字段',
        icon: 'none'
      });
      return;
    }
    
    const app = getApp();
    app.request(`/admin/schools/${editSchool.id}`, 'PUT', editSchool, 
      (res) => {
        if (res.code === 200) {
          wx.showToast({
            title: '学校信息更新成功',
            icon: 'success'
          });
          this.hideEditSchoolModal();
          this.getSchools();
        } else {
          wx.showToast({
            title: res.message || '更新学校失败',
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

  // 确认删除学校
  confirmDeleteSchool: function(e) {
    const schoolId = e.currentTarget.dataset.id;
    this.setData({
      showDeleteModal: true,
      deleteSchoolId: schoolId
    });
  },

  // 隐藏删除模态框
  hideDeleteModal: function() {
    this.setData({
      showDeleteModal: false,
      deleteSchoolId: null
    });
  },

  // 删除学校
  deleteSchool: function() {
    const schoolId = this.data.deleteSchoolId;
    
    const app = getApp();
    app.request(`/admin/schools/${schoolId}`, 'DELETE', null, 
      (res) => {
        if (res.code === 200) {
          wx.showToast({
            title: '学校删除成功',
            icon: 'success'
          });
          this.hideDeleteModal();
          this.getSchools();
        } else {
          wx.showToast({
            title: res.message || '删除学校失败',
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

  // 导航到学校账户管理页面
  navigateToSchoolAccounts: function(e) {
    const schoolId = e.currentTarget.dataset.id;
    const schoolName = e.currentTarget.dataset.name;
    wx.navigateTo({
      url: `/pages/admin/school_accounts/school_accounts?schoolId=${schoolId}&schoolName=${schoolName}`
    });
  }
});
