function captureLichHoc(){
    html2canvas($("#LichHoc"), {
      onrendered: function(canvas) {
    	  
    	  var img = canvas.toDataURL();
    	  location.href = img;

      }
    });
  }
function captureLichThi12(){
    html2canvas($("#calendar12"), {
      onrendered: function(canvas) {
    	  var img = canvas.toDataURL();
    	  location.href = img;

      }
    });
  }
function captureLichThi11(){
    html2canvas($("#calendar"), {
      onrendered: function(canvas) {
    	  var img = canvas.toDataURL();
    	  location.href = img;

      }
    });
  }
/* Attach a submit handler to the form */
$(document).ready(function() {
$("#ChangedMarkform").submit(function(event) {

    /* Stop form from submitting normally */
    event.preventDefault();

    /* Get some values from elements on the page: */
    var values = $(this).serialize();
    $("#ChangedMarkBotton").hide();
    $("#restore").hide();
    $("#waitingbardiv").show();
    /* Send the data using post and put the results in a div */
    $.ajax({
        url: "/changeMark",
        type: "POST",
        data: values,
        dataType: 'json',
        success: function(data,status) {
            $("#ChangedMarkBotton").show();
            $("#restore").show();
            $("#waitingbardiv").hide();
        	$("#mark4").text(data.GPA);
        	$("#Overal").text(data.Overal);
        	$("#FinishedCredit").text(data.FinishedCredit);
        	window.location.replace("/#GPA")
        	
          },

    });
});
});

function captureGPA(){
	html2canvas($('#GPA'), {
		   onrendered: function(canvas) {
		     var img = canvas.toDataURL();
		     window.open(img);
		  }
		});
    }
function captureschedule(){
	html2canvas($('#schedule'), {
		   onrendered: function(canvas) {
		     var img = canvas.toDataURL();
		     window.open(img);
		  }
		});
    }
function captureExamSchedule(){
	html2canvas($('#ExamSchedule'), {
		   onrendered: function(canvas) {
		     var img = canvas.toDataURL();
		     window.open(img);
		  }
		});
    }

function mark4Mess(mark,RC){
	if (mark > 4){Mess = 'Xời ơi! Không thể đâu';}
	else if (mark < 0){Mess = 'Kết quả âm, vui lòng nhập lại';}
	else if (mark >=3.5){var a = 4.0; var b = 3.5; Mess =  calu(a,b,mark,RC);}
	else if (mark >=3.0){var a = 3.5; var b = 3.0; Mess =  calu(a,b,mark,RC);}
	else if (mark >=2.5){var a = 3.0; var b = 2.5; Mess =  calu(a,b,mark,RC);}
	else if (mark >=2.0){var a = 2.5; var b = 2.0; Mess =  calu(a,b,mark,RC);}
	else if (mark >=1.5){var a = 2.0; var b = 1.5; Mess =  calu(a,b,mark,RC);}
	else if (mark >=1.0){var a = 1.5; var b = 1.0; Mess =  calu(a,b,mark,RC);};
	
	return Mess;
	}

function calu(a,b,mark,RC_){
	var y = RC_*(mark - a)/(b-a);
	var x = RC_ - y;
	var x = x.toFixed(0);
	var y = y.toFixed(0);	
	
	mess =  mark +' - Tương đương '+x+' tín chỉ '+a+' điểm và '+y+' tín chỉ '+b+' điểm';
	return mess;
}
