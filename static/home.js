			let curr = 0
			document.querySelector("img").addEventListener("click",toggleState);
			document.querySelector("button").addEventListener("click",parser);
			document.querySelector("body").addEventListener("keypress",feedSelector);
			mydivs = document.querySelectorAll(".circle")
			mydivs[0].addEventListener("click",firstFeed);
			mydivs[1].addEventListener("click",secondFeed);
			mydivs[2].addEventListener("click",thirdFeed);
			
			function firstFeed(){
				curr = 0
				$.ajax({
					url: '/switch',
					contentType: 'application/json;charset=UTF-8',
					data: JSON.stringify({'selector':curr}),
					type: 'POST',
					sucess: function(response){
					console.log(response);
					},
					error: function(error){
						console.log(error);
					}
				});
				changeSelectorColor(curr)
				
				
			}
			function secondFeed(){
				curr = 1
				$.ajax({
					url: '/switch',
					contentType: 'application/json;charset=UTF-8',
					data: JSON.stringify({'selector':curr}),
					type: 'POST',
					sucess: function(response){
					console.log(response);
					},
					error: function(error){
						console.log(error);
					}
				});
				changeSelectorColor(curr)
				
				
			}
			
			function thirdFeed(){
				curr = 2
				$.ajax({
					url: '/switch',
					contentType: 'application/json;charset=UTF-8',
					data: JSON.stringify({'selector':curr}),
					type: 'POST',
					sucess: function(response){
					console.log(response);
					},
					error: function(error){
						console.log(error);
					}
				});
				changeSelectorColor(curr)
				
				
			}
			
			function parser(){
				var inputHandler = document.querySelectorAll("input");
				if(inputHandler[1].value.split('x').length < 2){
					alert("Please provide resolution in ex.) 640x480");
					return;
				}
				data = {"fps": inputHandler[0].value ,"res":inputHandler[1].value,"brightness":inputHandler[2].value};
				$.ajax({
					url: '/api',
					contentType: 'application/json;charset=UTF-8',
					data: JSON.stringify(data),
					type: 'POST',
					sucess: function(response){
					console.log(response);
					},
					error: function(error){
						console.log(error);
					}
				});
				changeSelectorColor(curr);
				
			
			}

			
			function feedSelector(e){


				if(e.code == "Space"){
					
					++curr;
					if(curr > 2){
						curr = 0;
					}
					
					$.ajax({
						url: '/switch',
						contentType: 'application/json;charset=UTF-8',
						data: JSON.stringify({'selector':curr}),
						type: 'POST',
						sucess: function(response){
						console.log(response);
						},
						error: function(error){
							console.log(error);
						}
					});
					
					changeSelectorColor(curr)
					

										
				}
			
			
			}
			
			function changeSelectorColor(curr){
					var divs = document.querySelectorAll(".circle");
					divs[curr].style.backgroundColor = "red";
					if(curr === 0){
						divs[1].style.backgroundColor = "white";
						divs[2].style.backgroundColor = "white";
						
					}
					else if(curr === 1){
						divs[0].style.backgroundColor = "white";
						divs[2].style.backgroundColor = "white";
					}
					else if(curr === 2){
						divs[0].style.backgroundColor = "white";
						divs[1].style.backgroundColor = "white";
						divs[2].style.backgroundColor = "red";
						
					}				
				
				
			}

			function toggleState(){
				var img1= document.querySelector("img");
				if(img1.style.width == "75%"){
					img1.style.width = '50%';
					img1.style.height = "30%"
				}
				else{
					img1.style.width = "75%";
					img1.style.height = "50%";
				}
				

			}

			

		