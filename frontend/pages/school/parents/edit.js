Page({
  data: {
    parentId: null,
    parent: {
      nickname: '',
      phones: [''],
      remark: ''
    },
    createOrder: false,
    orderAmount: '',
    lessonCount: '',
    courseName: ''
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
        const parentData = res.data || {
          nickname: '',
          phones: [''],
          remark: '',
          orders: []
        };
        
        // 检查是否有订单信息
        let createOrder = false;
        let orderAmount = '';
        let lessonCount = '';
        let courseName = '';
        
        if (parentData.orders && parentData.orders.length > 0) {
          createOrder = true;
          const order = parentData.orders[0];
          orderAmount = order.amount || '';
          if (order.lesson_packages && order.lesson_packages.length > 0) {
            const lessonPackage = order.lesson_packages[0];
            lessonCount = lessonPackage.total_lessons || '';
            courseName = lessonPackage.course_name || '';
          }
        }
        
        this.setData({
          parent: parentData,
          createOrder: createOrder,
          orderAmount: orderAmount,
          lessonCount: lessonCount,
          courseName: courseName
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

  // 切换是否创建订单
  toggleCreateOrder: function(e) {
    this.setData({
      createOrder: e.detail.value
    });
  },

  // 输入订单金额
  inputOrderAmount: function(e) {
    this.setData({
      orderAmount: e.detail.value
    });
  },

  // 输入课时数量
  inputLessonCount: function(e) {
    this.setData({
      lessonCount: e.detail.value
    });
  },

  // 输入课程名称
  inputCourseName: function(e) {
    this.setData({
      courseName: e.detail.value
    });
  },

  // 保存家长信息
  saveParent: function() {
    const { parentId, parent, createOrder, orderAmount, lessonCount, courseName } = this.data;
    
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
    
    // 构建请求数据
    let requestData = { ...parent };
    
    // 如果需要关联订单，添加订单相关参数
    if (createOrder) {
      requestData.create_order = true;
      if (orderAmount) {
        requestData.order_amount = parseFloat(orderAmount);
      }
      if (lessonCount) {
        requestData.lesson_count = parseInt(lessonCount);
      }
      if (courseName) {
        requestData.course_name = courseName;
      }
    }
    
    app.request(url, method, requestData, res => {
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