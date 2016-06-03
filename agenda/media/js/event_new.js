(function() {
   // the DOM is available here

   // TinyMCE configuration for event's description field
   tinymce.init({
      selector:'#id_description',
      theme: 'modern',
      width: 600,
      height: 300,
      plugins: [
        'advlist autolink link image lists preview hr anchor pagebreak',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
        'save table contextmenu directionality emoticons paste textcolor'
      ],
      content_css: 'css/content.css',
      toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | print preview media fullpage | forecolor backcolor emoticons'
   });

})();


