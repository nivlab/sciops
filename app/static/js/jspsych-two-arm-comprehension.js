/**
 * jspsych-two-arm-comprehension
 * Sam Zorowitz
 *
 * plugin for running the comprehension check for the 2-arm bandit task
 *
 **/

jsPsych.plugins['two-arm-comprehension'] = (function() {
  var plugin = {};

  plugin.info = {
    name: 'two-arm-comprehension',
    description: '',
    parameters: {
      button_label: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Button label',
        default:  'Continue',
        description: 'Label of the button.'
      }
    }
  }
  plugin.trial = function(display_element, trial) {

    // Plug-in setup
    var plugin_id_name = "jspsych-survey-multi-choice";
    var plugin_id_selector = '#' + plugin_id_name;
    var _join = function( /*args*/ ) {
      var arr = Array.prototype.slice.call(arguments, _join.length);
      return arr.join(separator = '-');
    }

    // ---------------------------------- //
    // Section 1: Define Prompts          //
    // ---------------------------------- //

    // Define comprehension check questions.
    var prompts = [
      "<b><i>True</i> or <i>False</i>:</b>&nbsp;&nbsp;Your goal is to catch as many fish as you can.",
      "<b><i>True</i> or <i>False</i>:</b>&nbsp;&nbsp;You are more likely to catch fish at some beaches than others.",
      "<b><i>True</i> or <i>False</i>:</b>&nbsp;&nbsp;Even at the best beach, you will sometimes catch trash.",
      "<b><i>True</i> or <i>False</i>:</b>&nbsp;&nbsp;You can catch fish at a closed beach.",
      "<b><i>True</i> or <i>False</i>:</b>&nbsp;&nbsp;The number of fish you catch will affect your final performance bonus.",
    ];

    // Define response options.
    var options = [
      ["True","False"],
      ["True","False"],
      ["True","False"],
      ["True", "False"],
      ["True","False"],
    ];

    // Define correct answers.
    var correct = [
      "True",
      "True",
      "True",
      "False",
      "True",
    ]

    // ---------------------------------- //
    // Section 2: Define HTML             //
    // ---------------------------------- //

    // Initialize HTML
    var html = "";

    // inject CSS for trial
    html += `<style>
    body {
      height: 100vh;
      max-height: 100vh;
      overflow: hidden;
      position: fixed;
      background-color: #fefdfd;
    }
    .comprehension-box {
      position: absolute;
      top: 10%;
      left: 50%;
      -webkit-transform: translate3d(-50%, 0, 0);
      transform: translate3d(-50%, 0, 0);
      width: 70%;
      height: 100%;
      background: #ffffff;
      line-height: 1.25em;
    }
    .jspsych-survey-multi-choice-question {
      margin-top: 0em;
      margin-bottom: 1.0em;
      text-align: left;
      padding-left: 2em;
      font-size: 1.33vw;
    }
    .jspsych-survey-multi-choice-horizontal .jspsych-survey-multi-choice-text {
      text-align: left;
      margin: 0em 0em 0em 0em
    }
    .jspsych-survey-multi-choice-horizontal .jspsych-survey-multi-choice-option {
      display: inline-block;
      margin: 0.33em 1em 0em 1em;
    }
    .jspsych-survey-multi-choice-option input[type='radio'] {
      margin-right: 0.5em;
      width: 1.2em;
      height: 1.2em;
    }
     </style>`;

    html += '<div class="fishing-wrap">';

    // form element
    var trial_form_id = _join(plugin_id_name, "form");
    display_element.innerHTML += '<form id="'+trial_form_id+'"></form>';

    // Show preamble text
    html += '<div class="comprehension-box">'
    html += '<div class="jspsych-survey-multi-choice-preamble"><h4>Please answer the questions below:<br><small>You must answer all questions correctly to proceed.</small></h4></div>';

    // Initialize form element
    html += '<form id="jspsych-survey-multi-choice-form">';

    // Iteratively add comprehension questions.
    for (i = 0; i < prompts.length; i++) {

      // Initialize item
      html += `<div id="jspsych-survey-multi-choice-${i}" class="jspsych-survey-multi-choice-question jspsych-survey-multi-choice-horizontal" data-name="Q${i}">`;

      // Add question text
      html += `<p class="jspsych-survey-multi-choice-text survey-multi-choice">${prompts[i]}</p>`;

      // Iteratively add options.
      for (j = 0; j < options[i].length; j++) {

        // Option 1: True
        html += `<div id="jspsych-survey-multi-choice-option-${i}-${j}" class="jspsych-survey-multi-choice-option">`;
        html += `<input type="radio" name="jspsych-survey-multi-choice-response-${i}" id="jspsych-survey-multi-choice-response-${i}-${j}" value="${options[i][j]}" required>`;
        html += `<label class="jspsych-survey-multi-choice-text" for="jspsych-survey-multi-choice-response-${i}-${j}">${options[i][j]}</label>`;
        html += '</div>';

      }

      // Close item
      html += '<br></div>';

    }

    // add submit button
    html += '<input type="submit" id="'+plugin_id_name+'-next" class="'+plugin_id_name+' jspsych-btn"' + (trial.button_label ? ' value="'+trial.button_label + '"': '') + '"></input>';

    // End HTML
    html += '</form>';
    html += '</div></div>';

    // Display HTML
    display_element.innerHTML = html;

    // ---------------------------------- //
   // Section 2: jsPsych Functions       //
   // ---------------------------------- //

   // Detect submit button press
   document.querySelector('form').addEventListener('submit', function(event) {
     event.preventDefault();

     // Measure response time
     var endTime = performance.now();
     var response_time = endTime - startTime;

     // Gather responses
     var responses = [];
     var num_errors = 0;
     for (var i=0; i<prompts.length; i++) {

       // Find matching question.
       var match = display_element.querySelector('#jspsych-survey-multi-choice-'+i);
       var val = match.querySelector("input[type=radio]:checked").value;

       // Store response
       responses.push(val)

       // Check accuracy
       if ( correct[i] != val ) {
         num_errors++;
       }

     }

     // store data
     var trial_data = {
       "responses": responses,
       "num_errors": num_errors,
       "rt": response_time
     };

     // clear html
     display_element.innerHTML += '';

     // next trial
     jsPsych.finishTrial(trial_data);

   });

   var startTime = performance.now();
 };

 return plugin;
})();
