package com.example.volleyfetchjson;

import android.content.Context;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class VolleyUtil {
    String[] questions = new String[10];
    String[][] answers = new String[10][4];
    String[] correct_answer = new String[10];

    public void get(Context context, String url, final VolleyCallback callback){
        RequestQueue requestQueue = Volley.newRequestQueue(context);
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
            @Override
            public void onResponse(JSONObject response) {
                try {
                    // parse the JSON object
                    JSONArray jsonArray = response.getJSONArray("results");
                    for(int i = 0; i < 10; i++){
                        JSONObject q = jsonArray.getJSONObject(i);
                        questions[i] = q.getString("question");
                        correct_answer[i] = q.getString("correct_answer");
                        answers[i][0] = q.getString("correct_answer");
                        answers[i][1] = q.getJSONArray("incorrect_answers").getString(0);
                        answers[i][2] = q.getJSONArray("incorrect_answers").getString(1);
                        answers[i][3] = q.getJSONArray("incorrect_answers").getString(2);
                    }

                    callback.onSuccess(questions, answers, correct_answer);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
            }
        });
        requestQueue.add(jsonObjectRequest);
    }

    public interface VolleyCallback{
        void onSuccess(String[] questions, String[][] answers, String[] correct_answer);
    }
}
