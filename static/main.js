var USERNAME;

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
	SocketMgr.socket.on("clear",function(data) {
	    Canvas.ctx.clearRect(0,0,1000,800);
	});
	SocketMgr.socket.on("connect",function(data) {
	    USERNAME = data;
	});
    },
};

var Canvas = {
    canv: null,
    panel: null,
    wrapper: null,
    ctx: null,
    isTurn: null,
    init: function() {
	//initializing canvas settings
	this.canv = document.getElementById("canv");
	this.panel = document.getElementById("canvas-panel");
	this.wrapper = document.getElementById("canvas-wrapper");
	this.canv.width = 1000;
	this.canv.height = 800;
	this.ctx = this.canv.getContext("2d");
	this.ctx.lineWidth = 3;
	this.ctx.fillStyle = "#000";
	this.ctx.strokeStyle = "#000";
	//this.canv.imageSmoothingEnabled = false;
    },
    bindCanvasEvents: function() {
	var computeCanvasCoords = function(ix,iy) {
	    var cx = parseInt(getComputedStyle(Canvas.canv).width);
	    var cy = parseInt(getComputedStyle(Canvas.canv).height);
	    console.log("cy: "+cy);
	    var x = (ix - Canvas.wrapper.offsetLeft) / cx * 1000;
	    var y = ((iy - (window.innerHeight - cy)/2)) / cy * 800;
	    console.log("x: "+x+", "+"y: "+y);
	    return {x:x,y:y};
	};
      	var fx = function(e) {
	    console.log("e.clientX: "+e.clientX+", e.clientY: "+e.clientY);
	    var coords = computeCanvasCoords(e.clientX,e.clientY);
	    SocketMgr.socket.emit("draw",{x:coords.x,y:coords.y,isDrawing:true});
	    Canvas.ctx.lineTo(coords.x,coords.y);
      	    Canvas.ctx.stroke();
        };	
      	Canvas.canv.addEventListener("mousedown",function(e) {
	    var coords = computeCanvasCoords(e.clientX,e.clientY);
	    SocketMgr.socket.emit("draw",{x:coords.x,y:coords.y,isDrawing:false});
	    Canvas.canv.style.cursor = "sw-resize";
      	    Canvas.ctx.beginPath();
	    Canvas.ctx.moveTo(coords.x,coords.y);
      	    Canvas.canv.addEventListener("mousemove",fx);
	    Canvas.canv.addEventListener("mouseoff",function() {
		Canvas.ctx.stroke();
		Canvas.ctx.closePath();
	    });
	    Canvas.canv.addEventListener("mouseover",function(e) {
		var coords = computeCanvasCoords(e.clientX,e.clientY);
		Canvas.ctx.beginPath();
		Canvas.ctx.moveTo(coords.x,coords.y);
	    });
      	});
      	document.addEventListener("mouseup",function() {
      	    Canvas.canv.removeEventListener("mousemove",fx);
      	    Canvas.ctx.closePath();
	    Canvas.canv.style.cursor = "auto";
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
    var width = window.innerWidth - (300 + 15 + 15); //width of viewport minus sidebar and margin
    Canvas.wrapper.style.width = Math.max(375,Math.min(width,1000))+"px";
    Canvas.wrapper.style.height = "100%";
    Canvas.wrapper.style.left = (window.innerWidth - (300 + parseInt(Canvas.wrapper.style.width,10)))/2+"px";
    Canvas.panel.style.width = "100%";
    Canvas.panel.style.height = Math.max(300,Math.min((width * 0.8),800))+"px";
};

var bindMiscEvents = function() {
    var field = document.getElementById("chat-field");
    field.addEventListener("keypress", function(e) {
	if (e.which == 13 && !e.shiftKey && field.value != "") {
	    var data = field.value;
	    SocketMgr.socket.emit("message",data);
	    field.value = "";
	    var elem = document.createElement("p");
	    elem.innerHTML = data;
	    document.getElementById("chat-display").appendChild(elem);
	}
    });
    window.addEventListener("resize", initStyle);
    var board = document.getElementById("erase-board");
    board.addEventListener("mouseover",function() {
	this.innerHTML = "[X] erase board";
    });
    board.addEventListener("mouseout",function() {
	console.log("hey");
	this.innerHTML = "[X]";
    });
    board.addEventListener("click",function() {
	SocketMgr.socket.emit("clear",{hey:"hey"});
	Canvas.ctx.clearRect(0,0,1000,800);
    });
};

var pulseIndicator = function(str) {
    var ind = document.getElementById("floating-indicator");
    var txt = document.getElementById("indicator-text");
    txt.innerHTML = str;
    ind.style.opacity = "1";
    setTimeout(function(){ind.style.opacity="0";}, 3500);
};

var init = function() {
    SocketMgr.init();
    Canvas.init();
    SocketMgr.bindSocketEvents();
    initStyle();
    Canvas.bindCanvasEvents();
    bindMiscEvents();
};
