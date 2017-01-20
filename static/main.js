var SocketMgr = {
    socket: null,
    init: function() {
	//var for socket connection
	SocketMgr.socket = io.connect("127.0.0.1:5000");
    },
    bindSocketEvents: function() {
	SocketMgr.socket.on("buf",function(data) {
	    Canvas.draw(data);
	});
	SocketMgr.socket.on("chat",function(data) {
	    var elem = document.createElement("p");
	    elem.innerHTML = data;
	    document.getElementById("chat-display").appendChild(elem);
	});
    },
};

var Canvas = {
    canv: null,
    ctx: null,
    init: function() {
	//initializing canvas settings
	this.canv = document.getElementById("canv");
	this.canv.width = 1000;
	this.canv.height = 800;
	this.ctx = this.canv.getContext("2d");
	this.ctx.lineWidth = 3;
	this.ctx.fillStyle = "#000";
	this.ctx.strokeStyle = "#000";
	this.canv.imageSmoothingEnabled = false;
    },
    bindCanvasEvents: function() {
      	var fx = function(e) {
	    var canv = document.getElementById("canv");
	    var cx = parseInt(getComputedStyle(canv).width);
	    var cy = parseInt(getComputedStyle(canv).height);
	    //console.log("cx: "+cx);
	    var x = (e.clientX / cx) * 1000;
	    var y = (e.clientY / cy) * 800;
	    console.log("x: "+x+", "+"y: "+y);
	    //SocketMgr.socket.emit("draw",{x:e.clientX,y:e.clientY,isDrawing:true});
	    SocketMgr.socket.emit("draw",{x:x,y:y,isDrawing:true});
      	    //Canvas.ctx.lineTo(e.clientX,e.clientY);
	    Canvas.ctx.lineTo(x,y);
      	    Canvas.ctx.stroke();
        };	
      	Canvas.canv.addEventListener("mousedown",function(e) {
	    var canv = document.getElementById("canv");
	    var cx = parseInt(getComputedStyle(canv).width);
	    var cy = parseInt(getComputedStyle(canv).height);
	    var x = (e.clientX / cx) * 1000;
	    var y = (e.clientY / cy) * 800;
	    //SocketMgr.socket.emit("draw",{x:e.clientX,y:e.clientY,isDrawing:false});
	    SocketMgr.socket.emit("draw",{x:x,y:y,isDrawing:false});
      	    Canvas.ctx.beginPath();
      	    //Canvas.ctx.moveTo(e.clientX,e.clientY);
	    Canvas.ctx.moveTo(x,y);
      	    Canvas.canv.addEventListener("mousemove",fx);
	    Canvas.canv.addEventListener("mouseoff",function() {
		Canvas.ctx.stroke();
		Canvas.ctx.closePath();
	    });
	    Canvas.canv.addEventListener("mouseover",function(e) {
		var canv = document.getElementById("canv");
		var cx = parseInt(getComputedStyle(canv).width);
		var cy = parseInt(getComputedStyle(canv).height);
		var x = (e.clientX / cx) * 1000;
		var y = (e.clientY / cy) * 800;
		Canvas.ctx.beginPath();
		Canvas.ctx.moveTo(x,y);
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

var initStyle = function() {
    var canv = document.getElementById("canv");
    var panel = document.getElementById("canvas-panel");
    var wrap = document.getElementById("canvas-wrapper");
    //console.log(panel);
    //canv.style.width = "100%";
    //canv.style.height = "100%";
    var width = window.innerWidth - (300 + 15 + 15); //width of viewport minus sidebar and margin
    wrap.style.width = width+"px";
    wrap.style.height = "100%";
    panel.style.width = width+"px";
    panel.style.height = (width * 0.8)+"px";
    //console.log(panel.style);
};

var bindMiscEvents = function() {
    var field = document.getElementById("chat-field");
    field.addEventListener("keypress", function(e) {
	if (e.which == 13 && !e.shiftKey && field.value != "") {
	    console.log('ayy');
	    var data = field.value;
	    SocketMgr.socket.emit("message",data);
	    field.value = "";
	    var elem = document.createElement("p");
	    elem.innerHTML = data;
	    document.getElementById("chat-display").appendChild(elem);
	}
    });

    window.addEventListener("resize", initStyle);
};

var init = function() {
    SocketMgr.init();
    Canvas.init();
    SocketMgr.bindSocketEvents();
    initStyle();
    Canvas.bindCanvasEvents();
    bindMiscEvents();
};
