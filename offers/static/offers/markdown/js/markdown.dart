import 'dart:html';

void main(){  
  MarkdownHTMLConverter converter = new MarkdownHTMLConverter(".markdowntextfield", ".markdown-render");
  print(converter.getMarkdownContent());
}

class MarkdownHTMLConverter {
  TextAreaElement _textInput;
  DivElement _htmlOutputMaster;
  DivElement _renderedField;
  ButtonElement _refreshButton;
  
  MarkdownHTMLConverter(String textAreaClass, String divOutputClass){
    _textInput = querySelectorAll(textAreaClass)[0];
    _htmlOutputMaster = querySelectorAll(divOutputClass)[0];
    _htmlOutputMaster.appendHtml('<span class="title-text">Preview</span>');
    
    _refreshButton = new ButtonElement();
    _refreshButton.classes.addAll(["btn", "btn-success", "btn-xs", "pull-right"]);
    _refreshButton.text = "Refresh";
    _refreshButton.type = "button";
    _htmlOutputMaster.append(_refreshButton);

    _renderedField = new DivElement();
    _renderedField.classes.add("render-field");
    _renderedField.text = "Loaded";

    _htmlOutputMaster.append(_renderedField);
  }
  
  String getMarkdownContent(){
    return _textInput.text;
  }
}