LOGIN_STATUS = false;

$(function(){
  // API Calls
  function getLoginStatus(){
    $.ajax({
      // Gets the status of the login status of the user for our code to reference
      // Uppercase to symbolize global variables
      type: 'GET',
      dataType: "json",
      url: '/api/get-login-status',
      success: function (responseData) {
        if (responseData.status == true) {
          alert("You have logged in. Now you are able to use the history function");
          LOGIN_STATUS = true;
        }
      }
    });
  }

  function getHistory(){
      $.ajax({
        type: 'GET',
        dataType: "json",
        url: '/api/get-history',
        success: function (responseData) {
          $("#userHistory").empty();
          for(var i = 0; i < responseData.history.length ;i++){
            $("#userHistory").append("<p class='historyButtons btn btn-secondary prevPosts'>" + responseData.history[i] +"</p>");
          }
        }
      });
  }

  // Home page and actual calculations
  if (window.location.pathname == '/') {
    getLoginStatus();

    // Wait for getLoginStatus to finish before checking
    setTimeout(function(){
      if(LOGIN_STATUS){getHistory();}
    }, 1);

    // Links the enter key to the solve button
    window.addEventListener("keyup", function (e) {
      if (e.keyCode === 13) {
        solve.click();
      }
    });


    const initEquation = 'sqrt(75 / 3) + sin(x / 4)^2',
      expr = document.getElementById('expr'),
      pretty = document.getElementById('pretty'),
      result = document.getElementById('result'),
      solve = document.getElementById('solveButton'),
      expressionDropdown = document.getElementById('operationDropdown'),
      userHistory = document.getElementById('userHistory')

    var operationState = 'integrate',
      errors = document.getElementById('errors'),
      equationPost = initEquation, // Equation we will be posting
      validPost = true,
      parenthesis = 'keep',
      implicit = 'hide';

    // initialize with an example expression
    expr.value = initEquation;
    pretty.innerHTML = '$$\\int' + math.parse(expr.value).toTex({ parenthesis: parenthesis }) + ' dx$$';

    // Event Listeners
    $(expressionDropdown).on('change', updateLatex);    // Listens for a  change in the operation choice
    $(expr).on('keyup', updateLatex);                 // Listens for keypresses on the equation text
    $(userHistory).on('click', '.btn', function (e) {
      var temp = $(this).closest('.prevPosts')[0].innerText;
      expr.value = temp;
      updateLatex();
    });

    // Solves the equation by sending the information to backend for processing
    $(solve).on('click', function () {
      var answer = 0, errorMessage = "none";

      if (validPost) {
        var postData = {
          "equation": equationPost,
          "operation": expressionDropdown.value
        }
        // Sends a POST request to backend though AJAX
        // Uses the response to display the answer to the user
        $.ajax({
          type: 'POST',
          url: '/api/evaluate',
          contentType: 'application/json;charset=UTF-8',
          data: JSON.stringify(postData),
          success: function (responseData) {
            answer = responseData.answer;
              // Displays the integral
            if (expressionDropdown.value == 'integrate') {
              result.innerHTML = "[" + math.format(math.parse(answer)) + "] + C";
              // Displays the derivative
            } else if (expressionDropdown.value == 'derive') {
              result.innerHTML = math.format(math.parse(answer));
              // Displays an error message
            }
          }
        });

        // Posting equation to the history
        var obj = { "equation": equationPost };
        $.ajax({
          type: 'POST',
          url: '/api/update-history',
          contentType: 'application/json;charset=UTF-8',
          data: JSON.stringify(obj),
          // success: function (responseData) {
          //   console.log(responseData["status"])
          // }
        });

        getHistory();
      }
    });
    function updateLatex() {
      /*Shows what the user is typing and input validation*/
      var node = null;
      operationState = expressionDropdown.value;
      try {
        // parse the expression
        node = math.parse(expr.value);
        validPost = true;
        $(result).empty();


        // This is the part we send to the backend since it is the parsed equation
        equationPost = node.toString()
      }
      catch (err) {
        result.innerHTML = '<span style="color: red;">Syntax Error</span>';
        validPost = false;
      }

      try {
        // We check to see what kind of answer we display to the user
        if (operationState == 'integrate') {
          var latex = node ? "\\int" + node.toTex({ parenthesis: parenthesis }) + " dx" : '';
        } else if (operationState == 'derive') {
          var latex = node ? node.toTex({ parenthesis: parenthesis }) + " d/dx" : '';
        }
        // display and re-render the expression
        var elem = MathJax.Hub.getAllJax('pretty')[0];
        MathJax.Hub.Queue(['Text', elem, latex]);
      }
      catch (err) { }
    };
  } else if (window.location.pathname == '/login') {
    // Links the enter key to the submit button
    window.addEventListener("keyup", function(e){
      if(e.keyCode === 13){
        submitButton.click();
      }
    });
    var usernameInput = document.forms[0]["username"]
    var passwordInput = document.forms[0]["password"]

    const loginForm = document.forms[0]
    const submitButton = document.getElementById("loginButton");
    const loginErrorMessages = document.getElementById("loginFailedMessage");

    $(submitButton).on('click', function(){
      var obj = {
        "username": usernameInput.value,
        "password": passwordInput.value
      };
      // Submits login form to backend for error handling
      $.ajax({
        type: "POST",
        url: "/login",
        data: JSON.stringify(obj),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(responseData){
          if(responseData.errors.length == 0){
            $(loginErrorMessages).empty();
            window.location.href = "/";
          } else {
            $(loginErrorMessages).empty()
            for(var i = 0; i < responseData.errors.length; i++){
              $(loginErrorMessages).append("<p>" + responseData.errors[i] + "</p>");
            }
          }
        }
      })
    })
  } else if (window.location.pathname == '/register') {
    // Links the enter key to the register button
    window.addEventListener("keyup", function (e) {
      if (e.keyCode === 13) {
        registerButton.click();
      }
    });

    const registerButton = document.getElementById('registerButton'),
      name = document.getElementById('nameInput'),
      username = document.getElementById('usernameInput'),
      email = document.getElementById('emailInput'),
      password = document.getElementById('passwordInput'),
      confirmPassword = document.getElementById('confirmPasswordInput'),
      errorMessages = document.getElementById('errorMessages');

    $(registerButton).on('click', function(){
      $(errorMessages).empty();
      var obj = {
        'name': name.value,
        'username': username.value,
        'email': email.value,
        'password': password.value,
        'confirmPassword': confirmPassword.value
      }

      $.ajax({
        type: 'POST',
        url: '/register',
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(obj),
        success: function (responseData) {
          if(responseData.errorMessages.length == 0){
            LOGIN_STATUS = true;
            window.location.href = '/login';
          } else{
            for(var i = 0; i < responseData.errorMessages.length ;i++){
              $(errorMessages).append('<p>' + responseData.errorMessages[i] + '</p>');
            }
          };
        },
        error: function (responseData) {
          alert('error');
        }
      });
    });
  }
}
);
