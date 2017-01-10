var SocketMgr = {
    socket: null,
    init: function() {
	SocketMgr.socket = io.connect("127.0.0.1:5000");
    },
    bindSocketEvents: function() {
	SocketMgr.socket.on("buf",function(data) {
	    Canvas.draw(data);
	});
    },
};

var Canvas = {
    canv: null,
    ctx: null,
    /*buf: (function() {
	var items = [];
	return {
	    enqueue:  function(data) {
		items.push(data);
	    },
	    dequeue: function() {
		var temp = items[0];
		items.splice(1);
		return temp;
	    },
	    peek: function() {
		return items[0];
	    },
	    size: function() {
		return items.length;
	    }
	};
    }()),*/
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
      	});
      	Canvas.canv.addEventListener("mouseup",function() {
	    	//Canvas.draw.isDrawing = false;
	    	//SocketMgr.socket.emit("up");
      		Canvas.canv.removeEventListener("mousemove",fx);
      		Canvas.ctx.closePath();
      	});
    },
    draw: function(data) {
	//this.isDrawing = false;
	if (!(data.isDrawing)) {
	    Canvas.ctx.closePath();
	    Canvas.ctx.beginPath();
	    Canvas.ctx.moveTo(data[0].x,data[0].y);//Canvas.buf.peek().x,Canvas.buf.peek().y);
	}
	else {
	    Canvas.ctx.lineTo(data.x,data.y);
      	    Canvas.ctx.stroke();
	}
	/*for (var i=0; i<Canvas.buf.length; i++) {
	    var data = Canvas.buf[i];
	    Canvas.ctx.lineTo(data.x,data.y);
      	    Canvas.ctx.stroke();
	}*/
	/*while (data.length > 0) {
	    //var data = Canvas.buf.dequeue();
	    Canvas.ctx.lineTo(data.x,data.y);
      	    Canvas.ctx.stroke();
	    data.splice(1);
	}*/
    },
};

var init = function() {
    SocketMgr.init();
    Canvas.init();
    SocketMgr.bindSocketEvents();
    Canvas.bindCanvasEvents();
};
