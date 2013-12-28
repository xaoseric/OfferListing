import 'dart:html';
import 'dart:convert';
import 'dart:async';

void main(){  
  MarkdownHTMLConverter converter = new MarkdownHTMLConverter(".markdowntextfield", ".markdown-render");
}

class MarkdownHTMLConverter {
  TextAreaElement _textInput;
  DivElement _htmlOutputMaster;
  DivElement _renderedField;
  ButtonElement _refreshButton;
  String _csrfToken;
  
  var _refreshSubscription;
  
  MarkdownHTMLConverter(String textAreaClass, String divOutputClass){
    _textInput = querySelectorAll(textAreaClass)[0];
    _htmlOutputMaster = querySelectorAll(divOutputClass)[0];
    _htmlOutputMaster.appendHtml('<span class="title-text">Preview</span>');
    
    _refreshButton = new ButtonElement();
    _refreshButton.classes.addAll(["btn", "btn-success", "btn-xs", "pull-right"]);
    _refreshButton.text = "Refresh";
    _refreshButton.type = "button";
    _refreshButton.onClick.listen(_refreshButtonClick);
    _htmlOutputMaster.append(_refreshButton);

    _renderedField = new DivElement();
    _renderedField.classes.add("render-field");
    _renderedField.text = "Loaded";

    _htmlOutputMaster.append(_renderedField);

    // Get csrf token for post requests
    _csrfToken = querySelectorAll("[name=csrfmiddlewaretoken]")[0].value;
    
    // Set timers for rendering markdown
    _textInput.onKeyDown.listen(_textInputKeyDown);
    _textInput.onKeyUp.listen(_textInputKeyUp);
  }
  
  void _textInputKeyDown(Event e){
    _cancelMarkdownStream();
  }
  
  void _textInputKeyUp(Event e){
    _cancelMarkdownStream();
    var future = new Future.delayed(const Duration(milliseconds: 600));
    _refreshSubscription = future.asStream().listen((Stream stream) => refreshMarkdownContent());
  }
  
  void _cancelMarkdownStream(){
    if (_refreshSubscription != null){
      _refreshSubscription.cancel();
      _refreshSubscription = null;
    }
  }
  
  String getMarkdownContent(){
    return _textInput.value;
  }

  void _refreshButtonClick(Event e){
    _refreshButton.classes.add("disabled");
    refreshMarkdownContent();
  }
  
  void refreshMarkdownContent(){
    var url = "/helper/markdown/";
    
    FormData requestData = new FormData();
    requestData.append("markdown", getMarkdownContent());
    requestData.append("csrfmiddlewaretoken", _csrfToken);
    
    var request = HttpRequest.request(
        url,
        method: "POST",
        sendData: requestData
    ).then(_htmlContentReceived);
  }

  void _htmlContentReceived(HttpRequest request) {
    var responseData = JSON.decode(request.responseText);
    
    _renderedField.setInnerHtml(responseData["html"]);
    _refreshButton.classes.remove("disabled");
  }
}
