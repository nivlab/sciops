//------------------------------------//
// Define parameters.
//------------------------------------//

// Define context (color) assignment.
const contexts = jsPsych.randomization.shuffle(['red','green','blue']);
console.log(contexts)

// Define choices.
const choices = [37,38,39];

// Define timings.
// const choice_duration = 10000;
const choice_duration = null;

const feedback_duration = 2000;

// Define comprehension threshold.
const max_errors = 1;

// Define missed repsonses count.
var missed_threshold = 6;
var missed_responses = 0;

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

// Define forced choice trials.
var forced_choice_trials = [];

for (i = 0; i < 2; i++) {

  for (j = 0; j < 2; j++) {

    const trial = {
      type: 'three-arm-trial',
      beach_left: j % 2 == 0 ? contexts[i] : 'closed',
      beach_right: j % 2 == 1 ? contexts[i] : 'closed',
      outcome_left: j % 2 == 0 ? jsPsych.randomization.sampleWithoutReplacement(outcomes[i])[0] : -1,
      outcome_right: j % 2 == 1 ? jsPsych.randomization.sampleWithoutReplacement(outcomes[i])[0] : -1,
      choices: choices,
      choice_duration: choice_duration,
      feedback_duration: feedback_duration,
      data: {
        stimulus_L: j % 2,
        stimulus_R: 1 - j % 2,
        correct: choices[j % 2]
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
    forced_choice_trials.push(trial);

  }

}

// Randomize forced choice trials.
forced_choice_trials = jsPsych.randomization.repeat(forced_choice_trials, 2);

// Define trials.
var bandit_trials = [];

for (i = 0; i < 4; i++) {

  // Initialize set.
  const set = [];

  for (j = 0; j < 10; j++) {

    // Define trial.
    const trial = {
      type: 'three-arm-trial',
      beaches: contexts,
      outcome_left: i % 2 == 0 ? outcomes[j % 2][j] : outcomes[1 - j % 2][j],
      outcome_right: i % 2 == 1 ? outcomes[j % 2][j] : outcomes[1 - j % 2][j],
      choices: choices,
      choice_duration: choice_duration,
      feedback_duration: feedback_duration,
      data: {
        stimulus_L: i % 2 == 0 ? j % 2 : 1 - j % 2,
        stimulus_R: i % 2 == 1 ? j % 2 : 1 - j % 2,
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

  // Append two forced choice trials.
  set.push(forced_choice_trials[i*2]);
  set.push(forced_choice_trials[i*2+1]);

  // Randomize order.
  bandit_trials = bandit_trials.concat(jsPsych.randomization.shuffle(set));

}
