from form_create import get_forms_service_create
from form_response import get_forms_service_response
import qrcode

def google_form(subject, lecture_date_str, year, branch, start_time_str,division):
    forms_service = get_forms_service_create()
    # Request body for creating a form
    NEW_FORM = {
        "info": {
            "title": f"{subject} - Lecture Student Attendance Form",
            "documentTitle": f"Lecture Attendance for {subject} and {branch}" 

        }
    }

    NEW_INFO = {
  "requests": [
    {
      "updateFormInfo": {
        "info": {
          "description": f"Lecture details for {subject} on {lecture_date_str} ||  YEAR : {year} || Branch : {branch} || Division : {division} || Starting time : {start_time_str} " ,
          "title": f"{subject} - Lecture Student Attendance Form"
        },
        "updateMask": "*"
      }
    }
  ]
}
    # Request body to add a multiple-choice question
    NEW_QUESTION = {
  "requests": [
    {
      "createItem": {
        "item": {
          "title": "Student Name",

          "questionItem": {
            "question": {
              "textQuestion": {
                "paragraph": False
              }
            }
          }
        },
        "location": {
          "index": 0
        }
      }
    },

    {
      "createItem": {
        "item": {
          "title": "Enter Roll no",

          "questionItem": {
            "question": {
              "textQuestion": {
                "paragraph": False
              }
            }
          }
        },
        "location": {
          "index": 1
        }
      }
    }
    
  ]
}
    # Creates the initial form
    result = forms_service.forms().create(body=NEW_FORM).execute()

    # Adds the question to the form
    forms_service.forms().batchUpdate(formId=result["formId"], body=NEW_INFO).execute()
    forms_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTION).execute()
    
    get_result = forms_service.forms().get(formId=result["formId"]).execute()
    responder_url = get_result.get('responderUri', '')
    print(responder_url)
    print(result["formId"])
    # Generate QR code for the responder URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=5,
    )
    qr.add_data(responder_url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image
    img.save(f"static/{subject}_{year}-{branch}.png")

    return responder_url, result["formId"],get_result
