package ammannbros.garden_lighting_app;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.res.Configuration;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.view.View;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;


public class MainActivity extends FragmentActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.activity_main);


        final ProgressDialog progress = new ProgressDialog(this);
        progress.setTitle("Laden");
        progress.setMessage("Einen Moment bitte...");
        progress.show();

        final WebView web = (WebView) findViewById(R.id.webview);

        web.setVisibility(View.INVISIBLE);


        WebSettings webSettings = web.getSettings();
        webSettings.setJavaScriptEnabled(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                web.setVisibility(View.VISIBLE);
                progress.dismiss();
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                if (failingUrl.contains("garden-lighting")) {
                    web.loadUrl("http://" + "ammann.jumpingcrab.com:8080" + "/?token=vw3XoNJ37Nktmqj3b3ka_1eTOO8v3ZrC");
                }
            }
        });

        ConnectivityManager connManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo mWifi = connManager.getNetworkInfo(ConnectivityManager.TYPE_WIFI);

        String host;

        if (mWifi.isConnected()) {
            host = "loft:8080";
        } else {
            host = "ammann.jumpingcrab.com:8080";
        }

        web.loadUrl("http://" + host + "/?token=vw3XoNJ37Nktmqj3b3ka_1eTOO8v3ZrC");
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
    }
}