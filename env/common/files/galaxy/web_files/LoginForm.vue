
<template>
        <div class="row justify-content-md-center" style="width: 100%;">


<div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; position: absolute; left: 107px; top: 438px; gap: 8px; padding: 32px;">
    <div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; flex-grow: 0; flex-shrink: 0; width: 249.23px; position: relative; gap: 11px;">
        <p style="flex-grow: 0; flex-shrink: 0; font-size: 23px; text-align: left; color: #222;">
              About
        </p>
     </div>
     <div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; flex-grow: 0; flex-shrink: 0; width: 552px; position: relative; gap: 11px;">
        <p style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
              <span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
				  Fox is a powerful HPC-cluster available to all users of the Educloud Research infrastructure.
              </span>
              <br />
              <span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
                Educloud Research is a project-oriented self-service Platform as a Service that
                gives easy and fast access to a work environment for research projects, storage that
                is available from anywhere and low threshold HPC resources
              </span>
          </p>
     </div>
</div>

<div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; position: absolute; left: 780px; top: 438px; gap: 8px; padding: 32px;">
     <div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; flex-grow: 0; flex-shrink: 0; width: 249.23px; position: relative; gap: 11px;">
            <p style="flex-grow: 0; flex-shrink: 0; font-size: 23px; text-align: left; color: #222;">
              Getting started
            </p>
     </div>
     <div style="display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; flex-grow: 0; flex-shrink: 0; width: 552px; position: relative; gap: 11px;">
            <p style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
				<span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
					Apply for access to Educloud project ec73 (click on the Apply icon)
				</span>
				<br />
				<span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
					Install Google, Microsoft or another authenticator on your smartphone and scan the QR-code for 2 factor authentication (2FA).
                                        <a href="https://www.uio.no/english/services/it/research/platforms/edu-research/help/two-factor-authentication.html">See explanation here!</a>
				</span>
				<br />
				<span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
					Log in after your user and access to project ec73 is fixed
				</span>
				<br />
				<br />
				<span style="align-self: stretch; flex-grow: 0; flex-shrink: 0; width: 552px; font-size: 16px; text-align: left; color: #222;">
					If you have any questions, please write to hpc-drift@usit.uio.no
				</span>
            </p>
      </div>
</div>
      
<div style="width: 458px; height: 330px;">
	<img src="https://galaxy.educloud.no/static/galaxyFoxLogo.png" style="width: 458px; height: 330px; position: absolute; left: 200px; top: 50.5px; object-fit: none;"/>
</div>

<table>
    <tr>
	<th>
           <div class="row justify-content-md-center">
		 Login with your username and password
           </div>
	</th>
    </tr>
    <tr>
	<th>
            <template v-if="!confirmURL">
                      <b-form id="login" @submit.prevent="submitLogin()">
                                <div v-if="enableOidc" class="row justify-content-md-center">
                                    <!-- OIDC login-->
                                    <externalLogin :login_page="true" :exclude_idps="[connectExternalProvider]" />
                                </div>
                      </b-form>
            </template>
	</th>
    </tr>
    <tr>
	<th>
             <div class="row justify-content-md-center">
                Apply for access
             </div>
	</th>
    </tr>
    <tr>
	<th>
                       <div class="row justify-content-md-center">
                                <p></p>
                                  <a href="https://research.educloud.no/register"><img src="https://galaxy.educloud.no/static/apply-button.png" /></a>
                                <p></p>
                       </div>

	</th>
    </tr>
   <tr><th></th></tr>

</table>

        </div>
</template>


<script>
import axios from "axios";
import Vue from "vue";
import BootstrapVue from "bootstrap-vue";
import { withPrefix } from "utils/redirect";
import NewUserConfirmation from "./NewUserConfirmation";
import ExternalLogin from "components/User/ExternalIdentities/ExternalLogin";
import _l from "utils/localization";

Vue.use(BootstrapVue);

export default {
    components: {
        ExternalLogin,
        NewUserConfirmation,
    },
    props: {
        allowUserCreation: {
            type: Boolean,
            default: false,
        },
        enableOidc: {
            type: Boolean,
            default: false,
        },
        redirect: {
            type: String,
            default: null,
        },
        registrationWarningMessage: {
            type: String,
            default: null,
        },
        sessionCsrfToken: {
            type: String,
            required: true,
        },
        showWelcomeWithLogin: {
            type: Boolean,
            default: false,
        },
        termsUrl: {
            type: String,
            default: null,
        },
        welcomeUrl: {
            type: String,
            default: null,
        },
    },
    data() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            login: null,
            password: null,
            url: null,
            messageText: null,
            messageVariant: null,
            headerWelcome: _l("Welcome to Galaxy, please log in"),
            labelNameAddress: _l("Public Name or Email Address"),
            labelPassword: _l("Password"),
            confirmURL: urlParams.has("confirm") && urlParams.get("confirm") == "true",
            connectExternalEmail: urlParams.get("connect_external_email"),
            connectExternalProvider: urlParams.get("connect_external_provider"),
            connectExternalLabel: urlParams.get("connect_external_label"),
        };
    },
    computed: {
        welcomeUrlWithRoot() {
            return withPrefix(this.welcomeUrl);
        },
    },
    methods: {
        toggleLogin() {
            this.$emit("toggle-login");
        },
        submitLogin() {
            let redirect = this.redirect;
            if (this.connectExternalEmail) {
                this.login = this.connectExternalEmail;
            }
            if (localStorage.getItem("redirect_url")) {
                redirect = localStorage.getItem("redirect_url");
            }
            axios
                .post(withPrefix("/user/login"), {
                    login: this.login,
                    password: this.password,
                    redirect: redirect,
                    session_csrf_token: this.sessionCsrfToken,
                })
                .then(({ data }) => {
                    if (data.message && data.status) {
                        alert(data.message);
                    }
                    if (data.expired_user) {
                        window.location = withPrefix(`/root/login?expired_user=${data.expired_user}`);
                    } else if (this.connectExternalProvider) {
                        window.location = withPrefix("/user/external_ids?connect_external=true");
                    } else if (data.redirect) {
                        window.location = encodeURI(data.redirect);
                    } else {
                        window.location = withPrefix("/");
                    }
                })
                .catch((error) => {
                    this.messageVariant = "danger";
                    const message = error.response && error.response.data && error.response.data.err_msg;
                    if (this.connectExternalProvider && message && message.toLowerCase().includes("invalid")) {
                        this.messageText =
                            message + " Try logging in to the existing account through an external provider below.";
                    } else {
                        this.messageText = message || "Login failed for an unknown reason.";
                    }
                });
        },
        setRedirect(url) {
            localStorage.setItem("redirect_url", url);
        },
        resetLogin() {
            axios
                .post(withPrefix("/user/reset_password"), { email: this.login })
                .then((response) => {
                    this.messageVariant = "info";
                    this.messageText = response.data.message;
                })
                .catch((error) => {
                    this.messageVariant = "danger";
                    const message = error.response.data && error.response.data.err_msg;
                    this.messageText = message || "Password reset failed for an unknown reason.";
                });
        },
        returnToLogin() {
            window.location = withPrefix("/login/start");
        },
    },
};
</script>
<style scoped>
.form {
    background-color: rgb(173, 216, 230);
    padding: 100px;
    text-align: right;
    margin: auto;
    display: table;
}

th {
  padding: 15px;
}
</style>
