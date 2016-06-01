/*
* Github: https://github.com/cbertelegni/Simple-slide.js
*/

function simple_slide(app){
		app.lis=$("li", app.ul);
		app.w= $(app.lis[0]).width();
		app.wContent= app.lis.length * app.w;
		app.ul.css({ // set width para el ul
			"width": app.wContent + 30
		});
		app.next.click(function(){
			 moverUl(1);
			 return false;
		});
		app.prev.click(function(){
			 moverUl(0);
			 return false;
		});
		validaMarginUl();
	function moverUl(btn){
		if (btn) { //next
			var marginLeft="-="+app.w;
		}else{ // prev
			var marginLeft="+="+app.w;
		};
		app.ul.stop(0,1).animate({"margin-left": marginLeft},  200, app.efecto_animacion, function(){validaMarginUl()});
	}
	function validaMarginUl(){
		var marginUl = parseInt(app.ul.css("margin-left"));
		
		if(0 <= marginUl){
			app.ul.stop(0, 1).animate({"margin-left": 0}, 100);
			app.prev.hide();
		}else{
			app.prev.show();
		}
		if((marginUl + app.wContent) <= app.w ){
			app.ul.stop(0, 1).animate({"margin-left": (app.w -app.wContent)}, 100);
			app.next.hide();
		}else{
			app.next.show();
		}
	}
}