package com.example.volleyfetchjson;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.text.Html;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;


public class MainActivity extends AppCompatActivity implements View.OnClickListener {

    private TextView questionText;
    private Button button1, button2, button3, button4, correct;
    private Drawable d;


    // replace this url to change the category
    public String url = "https://opentdb.com/api.php?amount=10&type=multiple";

    private QuestionLib questionlib;

    private int currentQuestionNum = 0;
    private int score = 0;

    private ProgressBar progressBar;
    private CountDownTimer countDownTimer;

    private ImageButton imageButton;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // find all the views
        progressBar = findViewById(R.id.progressBar);
        questionText = findViewById(R.id.textView);
        imageButton = findViewById(R.id.imageButton);
        button1 = findViewById(R.id.button);
        button2 = findViewById(R.id.button2);
        button3 = findViewById(R.id.button3);
        button4 = findViewById(R.id.button4);
        // remember the original button background
        d = button1.getBackground();

        // all the Button onClick methods see below
        button1.setOnClickListener(this);
        button2.setOnClickListener(this);
        button3.setOnClickListener(this);
        button4.setOnClickListener(this);

    }

    public void onResume(){
        super.onResume();
        // use Volley to get 10 questions(and their answers) from the Open Trivia API and create a new question library for them
        VolleyUtil volleyUtil = new VolleyUtil();
        volleyUtil.get(this, url, new VolleyUtil.VolleyCallback() {
            @Override
            public void onSuccess(String[] questions, String[][] answers, String[] correct_answer) {
                questionlib = new QuestionLib(questions, answers, correct_answer);
                questionlib.shuffleAnswers();

                // show the first question and find the button with the correct answer
                updateQuestion(currentQuestionNum);
                findCorrectButton(currentQuestionNum);
                startCountdown();

            }
        });
    }

    // use Handler for a delayed task (here: to load the next question)
    final Handler handler = new Handler();
    final Runnable r = new Runnable() {
        @Override
        public void run() {

            updateQuestion(currentQuestionNum);
            changeColorBack();
            findCorrectButton(currentQuestionNum);
            activateButtons();
            startCountdown();

        }
    };
    
    @Override
    public void onClick(View v){

        switch(v.getId()){
            case R.id.button:
                countDownTimer.cancel();
                disableButtons();
                if(button1.getId() == correct.getId()){
                    button1.setBackgroundColor(Color.GREEN);
                    score++;
                    currentQuestionNum++;

                } else {
                    button1.setBackgroundColor(Color.RED);
                    correct.setBackgroundColor(Color.GREEN);
                    currentQuestionNum++;
                }

                // if all the questions are answered, game over
                // otherwise: after 1.5 seconds the next question will be loaded
                if(currentQuestionNum == 10){
                    gameOver();
                } else {
                    handler.postDelayed(r, 1500);
                }

                break;

            case R.id.button2:
                countDownTimer.cancel();
                disableButtons();
                if(button2.getId() == correct.getId()){
                    button2.setBackgroundColor(Color.GREEN);
                    score++;
                    currentQuestionNum++;

                } else {
                    button2.setBackgroundColor(Color.RED);
                    correct.setBackgroundColor(Color.GREEN);
                    currentQuestionNum++;
                }

                if(currentQuestionNum == 10){
                    gameOver();
                } else {
                    handler.postDelayed(r, 1500);
                }

                break;

            case R.id.button3:
                countDownTimer.cancel();
                disableButtons();
                if(button3.getId() == correct.getId()){
                    button3.setBackgroundColor(Color.GREEN);
                    score++;
                    currentQuestionNum++;

                } else {
                    button3.setBackgroundColor(Color.RED);
                    correct.setBackgroundColor(Color.GREEN);
                    currentQuestionNum++;
                }

                if(currentQuestionNum == 10){
                    gameOver();
                } else {
                    handler.postDelayed(r, 1500);
                }

                break;

            case R.id.button4:
                countDownTimer.cancel();
                disableButtons();
                if(button4.getId() == correct.getId()){
                    button4.setBackgroundColor(Color.GREEN);
                    score++;
                    currentQuestionNum++;

                } else {
                    button4.setBackgroundColor(Color.RED);
                    correct.setBackgroundColor(Color.GREEN);
                    currentQuestionNum++;
                }

                if(currentQuestionNum == 10){
                    gameOver();
                } else {
                    handler.postDelayed(r, 1500);
                }

                break;
        }

    }

    // update the questions and options for the current number
    // use Html.fromHtml to show the text correctly (otherwise: for example, a single quote will be showed as &#039)
    public void updateQuestion(int n){
        questionText.setText(Html.fromHtml(questionlib.getQuestions(currentQuestionNum)));
        button1.setText(Html.fromHtml(questionlib.getAnswer1(currentQuestionNum)));
        button2.setText(Html.fromHtml(questionlib.getAnswer2(currentQuestionNum)));
        button3.setText(Html.fromHtml(questionlib.getAnswer3(currentQuestionNum)));
        button4.setText(Html.fromHtml(questionlib.getAnswer4(currentQuestionNum)));

    }

    // because we have shuffled all the answers arrays, we don't know which button has the correct answer now
    // compare the button text with the correct answer to find the correct button
    public void findCorrectButton(int n){
        if(button1.getText().toString().equals(questionlib.getCorrect_answer(currentQuestionNum))) correct = findViewById(button1.getId());
        if(button2.getText().toString().equals(questionlib.getCorrect_answer(currentQuestionNum))) correct = findViewById(button2.getId());
        if(button3.getText().toString().equals(questionlib.getCorrect_answer(currentQuestionNum))) correct = findViewById(button3.getId());
        if(button4.getText().toString().equals(questionlib.getCorrect_answer(currentQuestionNum))) correct = findViewById(button4.getId());
    }

    // for the next question all the button background must be set back to origin
    public void changeColorBack(){
        button1.setBackground(d);
        button2.setBackground(d);
        button3.setBackground(d);
        button4.setBackground(d);
    }

    public void startCountdown(){
        countDownTimer = new CountDownTimer(10000 + 500, 100) {
            @Override
            public void onTick(long l) {
                int progress = (int) l / 100;
                progressBar.setProgress(progress);
            }

            @Override
            public void onFinish() {
                correct.setBackgroundColor(Color.GREEN);
                currentQuestionNum++;

                if(currentQuestionNum == 10){
                    gameOver();
                } else {
                    handler.postDelayed(r, 1500);
                }

            }
        };
        countDownTimer.start();
    }

    public void disableButtons(){
        button1.setClickable(false);
        button2.setClickable(false);
        button3.setClickable(false);
        button4.setClickable(false);
    }

    public void activateButtons(){
        button1.setClickable(true);
        button2.setClickable(true);
        button3.setClickable(true);
        button4.setClickable(true);
    }

    // show score when all 10 questions are answered
    public void gameOver(){
        Toast toast = Toast.makeText(this, "This is the end of the quiz! Your score: " + score, Toast.LENGTH_LONG );
        toast.show();
    }


}
