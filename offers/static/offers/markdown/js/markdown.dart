import 'dart:html';
import 'dart:convert';

void main(){  
  MarkdownHTMLConverter converter = new MarkdownHTMLConverter(".markdowntextfield", ".markdown-render");
  print(converter.getMarkdownContent());
}

class MarkdownHTMLConverter {
  TextAreaElement _textInput;
  DivElement _htmlOutputMaster;
  DivElement _renderedField;
  ButtonElement _refreshButton;
  String _csrfToken;
  
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
  }
  
  String getMarkdownContent(){
    return _textInput.text;
  }

  void _refreshButtonClick(Event e){
    _refreshButton.classes.add("disabled");
    refreshMarkdownContent();
  }
  
  void refreshMarkdownContent(){
    print("Going to refresh!");
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
    print(request.responseText);
    _refreshButton.classes.remove("disabled");
  }
}
