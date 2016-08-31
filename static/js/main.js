Dropzone.options.imageUploadZone = {
  init: function() {
    this.on("queuecomplete", function() {
      location.reload();
    });
  }
};
