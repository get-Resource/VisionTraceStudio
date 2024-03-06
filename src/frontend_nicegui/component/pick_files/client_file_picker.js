export default {
    template: `
      <q-uploader
        ref="uploader"
        :url="computed_url"
        @added="handleFileChange"
      >
        <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">
          <slot :name="slot" v-bind="slotProps || {}" />
        </template>
      </q-uploader>
    `,
    mounted() {
      setTimeout(() => this.compute_url(), 0); // NOTE: wait for window.path_prefix to be set in app.mounted()
    },
    updated() {
      this.compute_url();
    },
    methods: {
      compute_url() {
        this.computed_url = (this.url.startsWith("/") ? window.path_prefix : "") + this.url;
      },
      handleFileChange(files) {
        // 获取选择的文件列表
        this.files = files;
        // this.files = Array.from(event.target.files);
      },
      // 手动上传文件
      async uploadFiles(computed_url,parameter) {
        // 获取文件对象
        const uploader = this.$refs.uploader;
        if (uploader.queuedFiles.length > 0) {
            // 创建 FormData 对象，用于构建表单数据
            const formData = new FormData();
            // formData.append("files", uploader.queuedFiles);
            uploader.queuedFiles.forEach((file, index) => {
              formData.append("files", file);
            });
            // 循环遍历对象，并将键值对添加到 FormData 中
            for (const key in parameter) {
                if (Object.hasOwnProperty.call(parameter, key)) {
                    formData.append(key, parameter[key]);
                }
            }
            try {
                formData.append("start_time", new Date().toISOString());
                const response = await fetch(computed_url, {
                    method: 'POST',
                    mode: 'cors', // 添加这个选项以发送跨域请求
                    // headers: {
                    //   'Authorization': `Bearer ${token}` // 设置请求头部为 JSON 格式
                    // },
                    body: formData
                  })
                  if (response.ok) {
                      console.log("Files uploaded successfully");
                      // 遍历文件列表，并标记每个文件为已上传
                      uploader.queuedFiles.forEach(file => {
                        file.Uploaded = true;
                      });
                      // uploader.removeQueuedFiles()
                      return {code:1,message:"成功上传"}
                  } else {
                      console.error("Failed to upload files");
                      return {code:-1,message:"上传失败请检查参数问题"}
                  }
            }catch (error) {
                console.error('Error fetching data:', error);
                return {code:-1,message:"上传失败请检查网络问题:" + error}
            }
        }else{
            console.error("No file selected");
            return {code:1,message:"没有文件上传"}
        }
      }
    },
    props: {
      url: String,
    },
    data: function () {
      return {
        computed_url: this.url,
      };
    },
  };
  