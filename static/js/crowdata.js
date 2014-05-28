if(!console) console = {};
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

jQuery.fn.formatTextMillons = function(length){ /* format numbers to $ 100 M */
  var patt = /\$\s?([0-9\.]+)(\,[0-9]{2})?/gi;
  this.each(function(i, v) {
    $this = $(v);
    $this.text($this.text().replace(patt, function(match, group1, group2){
            var n = "$ ";
            if (group1.length > length){
                group1 = +group1.replace(/\./g, "");
                n += (group1/1000000).toFixed(2) + " M";
            }else{
                n = match;
            }  
            return  n
        }));
  });
};

function replace_txt_html(){ // replace html_entities tags in "{{{TAGS}}}" 
    if (!this.tags_txt) {
        this.find = "body :contains({{{)";
        this.tags_txt = $(this.find);
    }
    
    if (this.tags_txt.length){
      var last_link = this.tags_txt.last();
      var html = last_link.html()
                  .replace(/\{\{\{|\}\}\}/ig, "")
                  .replace(/\&lt\;/ig, "<")
                  .replace(/\&gt\;/ig, ">");
      last_link.html(html);
      this.tags_txt = $(this.find);
      if(this.tags_txt.length){replace_txt_html()};
    }
};

    
function create_sosial(cont_social, url, text, title){ // recibe the JQ content and url to share
    /* Exaple
    *
    * create_sosial($('.herramientasSociales.social'), location.href, "Liberá un documento!");
    *
    */
    
    if(!title) var title = document.title;
    if(!text) var text = title;
    if(!url) var url = location.href;
    
    // FB
    var face = $('<div class="col-md-3 fb-share-button facebookMeGusta" style="">'); 
        face.attr({
          "data-type": "box_count"
          // "data-href": url
        });
    var face_root = $('<div id="fb-root">');
    var face_js = $('<script src="//connect.facebook.net/es_LA/all.js#xfbml=1&status=0">');

    // TW

    var twitter = $('<a class="twitter-share-button" onclick="" href="" title="Twitter" style="" data-count="vertical">');
        twitter.attr({
          "data-url": url,
          "data-text": text
          // "data-hashtags": "VozData"
        })
        .html('Tweet');
    var wrap_tw = $('<div class="twitter col-md-3" style="">');
        
    var twitter_js = $('<script src="http://platform.twitter.com/widgets.js">');
        wrap_tw.append(twitter);

    // GOO+
    var gplus = $('<div class="google col-md-3" id="plusoneAcumulado" style="">');

    // MAIL
    var mail = $('<div class="compmail2 col-md-3" style="">');
        mail.append(
          $('<a class="enviar bot_mail2" title="Enviar">').attr("href", "mailto:?subject=" + title +"&body=" + text + " " + url)
          // .append($('<img src="" border="0">'))
            );
    
    cont_social.html("").append(face, face_root, face_js, wrap_tw, twitter_js, gplus, mail );
    
    gapi.plusone.render("plusoneAcumulado",{"size": "tall", "href": url});

  }

  /* Popup
  * var popup = new Popup();
  * popup.show_p({ 
  *     title: "Title of popup",
  *     body: "This is the content of body, it can be html",
  *     addclass: "class to add to '.popup_bg'"
  *   }, callback) // show popup
  * popup.hide_p(); // hide popup
  */
  function Popup(){
    var s = this;
    this.popup = $("#popup");
    this.popup_cont = $(".popup_cont");
    this.popup_title = $("b", this.popup_cont);
    this.popup_body = $(".popup_body", this.popup_cont);
    this.close = $("a.close", this.popup_cont);
    this.close.click(function(event) {
      s.hide_p();
    });
  }
  Popup.prototype.show_p = function(cont, callback){
    var s = this;
    this.popup_title.html(cont.title); // set title
    this.popup_body.html(cont.body); // set body
    this.addclass = cont.addclass || "";
    this.popup_cont.addClass(this.addclass);
    this.popup.show(0, function() { // swow
      s.popup_cont.fadeIn('slow');
      if(callback) callback();
    });
  }
  Popup.prototype.hide_p = function (callback){ // close popup
    var s = this;
    this.popup.fadeOut("fast", function(){
      s.popup_title.html(""); // set title
      s.popup_body.html(""); // set body   
      s.popup_cont.removeClass(s.addclass).hide();
      if(callback) callback();
    });
  }

  /* /Popup */
