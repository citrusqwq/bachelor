package com.example.volleyfetchjson;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class QuestionLib {
    private String[] questions;
    private String[][] answers;
    private String[] correct_answer;

    public QuestionLib(String[] questions, String[][] answers, String[] correct_answer){
        this.questions = questions;
        this.answers = answers;
        this.correct_answer = correct_answer;
    }

    public String getQuestions(int n) {
        return questions[n];
    }

    public String getCorrect_answer(int n) {
        return correct_answer[n];
    }

    public String getAnswer1(int n){
        return answers[n][0];
    }

    public String getAnswer2(int n){
        return answers[n][1];
    }

    public String getAnswer3(int n){
        return answers[n][2];
    }

    public String getAnswer4(int n){
        return answers[n][3];
    }

    // The original answer array is always in the same order: {correctAns, incorrectAns1, incorrectAns2, incorrectAns2}
    // shuffle the answers so that later the correct answer will be assigned to a random Button instead of always to Button1
    public void shuffleAnswers(){
        for(int i = 0; i <10; i++){
            List<String> list = new ArrayList<String>();
            list.add(this.answers[i][0]);
            list.add(this.answers[i][1]);
            list.add(this.answers[i][2]);
            list.add(this.answers[i][3]);
            Collections.shuffle(list);
            String[] newAnswers = list.toArray(new String[list.size()]);
            this.answers[i] = newAnswers;
        }
    }
}
