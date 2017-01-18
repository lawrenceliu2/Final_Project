var SocketMgr = {
    socket: null,
    init: function() {
	SocketMgr.socket = io.connect("127.0.0.1:5000");
    },
    bindSocketEvents: function() {
	SocketMgr.socket.on("buf",function(data) {
	    Canvas.draw(data);
	});
	SocketMgr.socket.on("chat",function(data) {
	    var elem = document.createElement("p");
	    //elem.style.margin = "0";//"15px 0 0 15px";
	    elem.innerHTML = data;
	    document.getElementById("chat-display").appendChild(elem);
	});
    },
};

var Canvas = {
    canv: null,
    ctx: null,
    init: function() {
	this.canv = document.getElementById("canv");
	this.canv.width = screen.width;
	this.canv.height = screen.height;
	this.ctx = this.canv.getContext("2d");
	this.ctx.lineWidth = 3;
	this.ctx.fillStyle = "#000";
	this.ctx.strokeStyle = "#000";
    },
    bindCanvasEvents: function() {
      	var fx = function(e) {
	    SocketMgr.socket.emit("draw",{x:e.clientX,y:e.clientY,isDrawing:true});
      	    Canvas.ctx.lineTo(e.clientX,e.clientY);
      	    Canvas.ctx.stroke();
        };	
      	Canvas.canv.addEventListener("mousedown",function(e) {
	    SocketMgr.socket.emit("draw",{x:e.clientX,y:e.clientY,isDrawing:false});
      	    Canvas.ctx.beginPath();
      	    Canvas.ctx.moveTo(e.clientX,e.clientY);
      	    Canvas.canv.addEventListener("mousemove",fx);
	    Canvas.canv.addEventListener("mouseoff",function() {
		//SocketMgr.socket.emit("draw",{x:e.clientX,y:e.clientY,isDrawing:false});
		Canvas.ctx.stroke();
		Canvas.ctx.closePath();
	    });
	    Canvas.canv.addEventListener("mouseover",function(e) {
		Canvas.ctx.beginPath();
		Canvas.ctx.moveTo(e.clientX,e.clientY);
	    });
      	});
      	document.addEventListener("mouseup",function() {
      		Canvas.canv.removeEventListener("mousemove",fx);
      		Canvas.ctx.closePath();
      	});
    },
    draw: function(data) {
	if (!(data.isDrawing)) {
	    Canvas.ctx.closePath();
	    Canvas.ctx.beginPath();
	    Canvas.ctx.moveTo(data.x,data.y);
	}
	else {
	    Canvas.ctx.lineTo(data.x,data.y);
      	    Canvas.ctx.stroke();
	}
    },
};

var bindMiscEvents = function() {
    var field = document.getElementById("chat-field");
    /*document.getElementById("msg_sub").addEventListener("click", function(e) {
	console.log('ayy');
	var data = field.value;
	SocketMgr.socket.emit("message",data);
	field.value = "";
	var elem = document.createElement("p");
	elem.style.margin = "0";//"15px 0 0 15px";
	elem.innerHTML = data;
	document.getElementById("chat-display").appendChild(elem);
    });*/
    field.addEventListener("keypress", function(e) {
	if (e.which == 13 && !e.shiftKey && field.value != "") {
	    console.log('ayy');
	    var data = field.value;
	    SocketMgr.socket.emit("message",data);
	    field.value = "";
	    var elem = document.createElement("p");
	    //elem.style.margin = "0";//"15px 0 0 15px";
	    //elem.style.fontFamily = "monospace";
	    elem.innerHTML = data;
	    document.getElementById("chat-display").appendChild(elem);
	}
    });
};

var init = function() {
    SocketMgr.init();
    Canvas.init();
    SocketMgr.bindSocketEvents();
    Canvas.bindCanvasEvents();
    bindMiscEvents();
};
