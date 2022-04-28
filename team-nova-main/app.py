from flask import Flask, request, redirect, url_for, render_template, session, make_response
from flask_session import Session
from datasheets import *
import sys

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["is_superuser"] = False
Session(app)

account_sid, auth_token = tuple(sys.argv[1:])
print(account_sid, auth_token)
datasheet = Datasheet(account_sid, auth_token) # this keeps track of all of the datasheets and other information


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/welcome")
def welcome():
    return render_template('welcome.html')


@app.route("/choice")
def choose_option():
    return render_template('data_or_messages.html')


@app.route("/view-data")
def view_data():
    main_chart_data, little_chart_data = datasheet.get_data_analytics()
    return render_template('view_data.html', main_chart_data=main_chart_data, little_chart_data=little_chart_data)


@app.route("/select-user")
def select_user():
    return render_template('user_selection.html')


@app.route("/table", methods=["GET", "POST"])
def table():
    is_superuser = session.get('is_superuser', None)
    print(is_superuser)
    if request.method == "POST":
        invaliddf=datasheet.send_messages(is_superuser)
        column_names = list(invaliddf.columns)
        num_rows = invaliddf.shape[0]
        num_cols = invaliddf.shape[1]
        df_as_list = invaliddf.values.tolist()
        return render_template('invalid.html', num_rows=num_rows, num_cols=num_cols, df=df_as_list, col_names=column_names)
    

    if is_superuser:
        df = datasheet.message_display_df()
    else:
        df = datasheet.user_message_display_df()
    column_names = list(df.columns)
    num_rows = df.shape[0]
    num_cols = df.shape[1]

    df_as_list = df.values.tolist()

    return render_template('table.html', num_rows=num_rows, num_cols=num_cols, df=df_as_list, col_names=column_names, is_superuser=is_superuser)

@app.route("/invalid")
def invalid():
    df=invaliddf
    column_names = list(df.columns)
    num_rows = df.shape[0]
    num_cols = df.shape[1]

    df_as_list = df.values.tolist()
    # resp = make_response(invaliddf.to_csv())
    # resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    # resp.headers["Content-Type"] = "text/csv"
    # return resp
    return render_template('invalid.html', num_rows=num_rows, num_cols=num_cols, df=df_as_list, col_names=column_names)


@app.route("/processing")
def processing():
    return redirect(url_for('choose_option'))


@app.route("/download")
def download():
    is_superuser = session.get('is_superuser', None)
    invaliddf=datasheet.send_messages(is_superuser)
    resp = make_response(invaliddf.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=invalid.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/superUploadASIMS", methods=["GET", "POST"])
def superUploadASIMS():
    is_superuser = True
    session['is_superuser'] = True
    if request.method == "POST":
        if request.files:
            if request.files["asims"].filename == "":
                err_message = ["Please upload a file before continuing"]
                return render_template('upload_1_supervisor.html', err=err_message)

            try:
                asims_spreadsheet = request.files["asims"]
                datasheet.process_upload_from_asims(asims_spreadsheet, True)
                return redirect(url_for('uploadphonenumbers'))

            except DatasheetsException as e:
                err_message = [e.message]
                return render_template('upload_1_supervisor.html', err=err_message)
            except:
                err_message = ["The datasheet is not formatted properly or doesn't contain enough information, please upload a new spreadsheet"]
                return render_template('upload_1_supervisor.html', err=err_message)

    return render_template('upload_1_supervisor.html')


@app.route("/userUploadASIMS", methods=["GET", "POST"])
def userUploadASIMS():
    session['is_superuser'] = False
    if request.method == "POST":

        if request.files:
            if request.files["asims"].filename == "":
                err_message = ["Please upload a file before continuing"]
                return render_template('upload_1_user.html', err=err_message)

            try:
                asims_spreadsheet = request.files["asims"]

                datasheet.process_upload_from_asims(asims_spreadsheet, False)

                datasheet.imr_df["Phone Number"] = "N/A"
                datasheet.due_df["Phone Number"] = "N/A"

                return redirect(url_for('enterphonenumbers'))
            except DatasheetsException as e:
                err_message = [e.message]
                return render_template('upload_1_user.html', err=err_message)
            except:
                err_message = ["The datasheet is not formatted properly or doesn't contain enough information, please upload a new spreadsheet"]
                return render_template('upload_1_user.html', err=err_message)


    return render_template('upload_1_user.html')


@app.route("/uploadphonenumbers", methods=["GET", "POST"])
def uploadphonenumbers():
    if request.method == "POST":
        if request.files:
            if request.files["phone_numbers"].filename == "":
                print("iuhiuhiuhiuh")
                err_message = ["Please upload a file before continuing"]
                return render_template('upload_2_supervisor.html', err=err_message)

            try:
                phone_number_spreadsheet = request.files["phone_numbers"]
                datasheet.process_upload_for_contact(phone_number_spreadsheet)

                return redirect(url_for('processing'))
            except DatasheetsException as e:
                err_message = [e.message]
                return render_template('upload_2_supervisor.html', err=err_message)


    return render_template('upload_2_supervisor.html')


@app.route("/enterphonenumbers", methods=["GET", "POST"])
def enterphonenumbers():

    imr_df = datasheet.imr_df
    due_df = datasheet.due_df

    airmen_due = datasheet.user_message_display_df()

    column_names = list(airmen_due.columns)
    num_rows = airmen_due.shape[0]
    num_cols = airmen_due.shape[1]

    df_as_list = airmen_due.values.tolist()

    if request.method == 'POST':
        for key in request.form:
            if key.startswith('number'):
                
                row = key.partition('.')[-1]
                phone_number = request.form[key]

                new_numbers = list(due_df['Phone Number'])
                new_numbers[int(row)] = phone_number
                # imr_df['Cell Phone Number'] = new_numbers
                due_df['Phone Number'] = new_numbers
                datasheet.due_df = due_df
                # session['imr_df'] = imr_df

                return redirect(url_for('enterphonenumbers'))
                              
    return render_template('upload_2_user.html', num_rows=num_rows, num_cols=num_cols, df=df_as_list, col_names=column_names)


@app.route("/notification-sucess")
def notification_success():
    print("notification success flask")
    return render_template('notification-success.html')

if __name__ == "__main__":
    app.run(debug=True)
