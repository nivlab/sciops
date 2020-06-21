//------------------------------------//
// Define parameters.
//------------------------------------//

// Define context (color) assignment.
const contexts = jsPsych.randomization.shuffle(['red','green','blue']);

// Define choices.
const choices = [37,38,39];    // left, top, right

// Define timings.
// const choice_duration = 10000;
const choice_duration = null;
const feedback_duration = 1500;

// Define comprehension threshold.
const max_errors = 1;

// Define missed repsonses count.
var missed_threshold = 6;
var missed_responses = 0;

//------------------------------------//
// Define images to preload.
//------------------------------------//

preload_images = [
  "../static/img/cloud01.svg",
  "../static/img/cloud02.svg",
  "../static/img/cloud03.svg",
  "../static/img/animal-fish01.svg",
  "../static/img/animal-tire.svg",
  "../static/img/animal-lion.svg",
  "../static/img/animal-snake.svg",
  "../static/img/surfboard-blue.svg",
  "../static/img/surfboard-green.svg",
  "../static/img/surfboard-red.svg",
  "../static/img/instructions01.png",
  "../static/img/instructions02.png",
  "../static/img/instructions03.png",
  "../static/img/instructions04.png",
  "../static/img/instructions05.png",
  "../static/img/instructions06.png",
  "../static/img/instructions07.png",
  "../static/img/instructions08.png",
  "../static/img/instructions09.png",
];

//------------------------------------//
// Define instructions block.
//------------------------------------//

// Define image scaling CSS.
const style = "width:auto; height:auto; max-width:100%; max-height:80vh;";

// Define instructions sequence.
var instructions = {
  type: 'instructions',
  pages: [
    `<img src='../static/img/instructions01.png' style="${style}"</img>`,
    `<img src='../static/img/instructions02.png' style="${style}"</img>`,
    `<img src='../static/img/instructions03.png' style="${style}"</img>`,
    `<img src='../static/img/instructions04.png' style="${style}"</img>`,
    `<img src='../static/img/instructions05.png' style="${style}"</img>`,
    `<img src='../static/img/instructions06.png' style="${style}"</img>`,
    `<img src='../static/img/instructions07.png' style="${style}"</img>`,
    `<img src='../static/img/instructions08.png' style="${style}"</img>`,
  ],
  show_clickable_nav: true,
  button_label_previous: "Prev",
  button_label_next: "Next"
}

// Define comprehension check.
var comprehension = {
  type: 'three-arm-comprehension'
}

// Define instructions loop.
var instructions_loop = {
  timeline: [
    instructions,
    comprehension
  ],
  loop_function: function(data) {

    // Extract number of errors.
    const num_errors = data.values().slice(-1)[0].num_errors;

    // Check if instructions should repeat.
    if (num_errors > max_errors) {
      return true;
    } else {
      return false;
    }

  }
}

// Define ready check.
var ready = {
  type: 'instructions',
  pages: [
    `<img src='../static/img/instructions09.png' style="${style}"</img>`,
  ],
  show_clickable_nav: true,
  button_label_previous: "Prev",
  button_label_next: "Next"
}

//------------------------------------//
// Define 2-arm bandit task.
//------------------------------------//
// The 2-arm bandit task consists of two arms with
// 70% and 30% reward probability, respectively.
// The task is comprised of 40 free choice trials
// and 8 forced choice trials. Outcomes are pseudo-
// randomly determined such that participants will
// experience 7 (3) wins for the better (worse) arm
// every 10 trials. Moreover, the bandits are left/right
// counterbalanced (including outcomes).

// Define outcomes.
const outcomes = [
  [1,1,1,1,1,1,1,0,0,0],
  [1,1,1,0,0,0,0,0,0,0]
]

// Define trials.
var bandit_trials = [];

for (i = 0; i < 4; i++) {

  // Initialize set.
  const set = [];

  for (j = 0; j < 10; j++) {

    // Define trial.
    const trial = {
      type: 'three-arm-trial',
      contexts: contexts,
      outcomes: [1,1,1],
      choices: choices,
      choice_duration: choice_duration,
      feedback_duration: feedback_duration,
      data: {
        correct: i % 2 == 0 ? choices[j % 2] : choices[1 - j % 2]
      },
      on_finish: function(data) {

        // Evaluate missing data
        if ( data.key == null ) {

          // Set missing data to true.
          data.missing = true;

          // Increment counter. Check if experiment should end.
          missed_responses++;
          if (missed_responses >= missed_threshold) {
            jsPsych.endExperiment();
          }

        } else {

          // Set missing data to false.
          data.missing = false;

          // Define accuracy.
          data.accuracy = data.key == data.correct;

        }

      }

    }

    // Define looping node.
    const trial_node = {
      timeline: [trial],
      loop_function: function(data) {
        return data.values()[0].missing;
      }
    }

    // Append trial.
    set.push(trial_node);

  }

  // Randomize order.
  bandit_trials = bandit_trials.concat(jsPsych.randomization.shuffle(set));

}
