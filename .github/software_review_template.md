## Review checklist for @[reviewer_username]

Background information for reviewers [here](https://www.usgs.gov/products/software/software-management/types-software-review)

*Please check off boxes as applicable, and elaborate in comments below. If minor issues are found, feel free to create a branch or fork the project for review and make suggested changes directly in the source code using a pull request*

- Code location [URL_to_repo](URL_to_repo)
- author @[your_username]

### Comment to Reviewer

Place any comments and other info the Reviewer may need here.

### Conflict of interest

- [ ] I confirm that I have no COIs with reviewing this work, meaning that there is no relationship with the product or the product's authors or affiliated institutions that could influence or be perceived to influence the outcome of the review (if you are unsure whether you have a conflict, please speak to your supervisor _before_ starting your review).

### Adherence to Fundamental Science Practices

- [ ] I confirm that I read and will adhere to the [Federal Source Code Policy for Scientific Software](https://www.usgs.gov/survey-manual/im-osqi-2019-01-review-and-approval-scientific-software-release) and relevant federal guidelines for approved software release as outlined in [SM502.1](https://www.usgs.gov/survey-manual/5021-fundamental-science-practices-foundation-policy#:~:text=Issuance%20Number:%20502.1.%20Subject:%20Fundamental%20Science%20Practices:%20Foundation%20Policy.%20Issuance) and [SM502.4](https://www.usgs.gov/survey-manual/5024-fundamental-science-practices-review-approval-and-release-information-products).

### Security Review

- [ ] No proprietary code is included
- [ ] No Personally Identifiable Information (PII) is included
- [ ] No other sensitive information such as data base passwords are included

### General checks

- [ ] **Repository:** Is the source code for this software available?
- [ ] **License:** Does the repository contain a plain-text LICENSE file?
- [ ] **Disclaimer:** Does the repository have the USGS-required provisional Disclaimer?
- [ ] **Contribution and authorship:** Has the submitting author made major contributions to the software? Does the full list of software authors seem appropriate and complete?
- [ ] **Code.json**: Does the repository have a code.json file?

### Documentation

- [ ] **A statement of need**: Do the authors clearly state what problems the software is designed to solve?
- [ ] **Installation instructions:** Is there a clearly-stated list of dependencies? Ideally these should be handled with an automated package management solution.
- [ ] **Example usage:** Do the authors include examples of how to use the software (ideally to solve real-world analysis problems)?
- [ ] **Functionality documentation:** Is the core functionality of the software documented to a satisfactory level (e.g., API method documentation)?
- [ ] **Automated tests:** Are there automated tests or manual steps described so that the functionality of the software can be verified?
- [ ] **Community guidelines**: Are there clear guidelines for third parties wishing to 1) Contribute to the software 2) Report issues or problems with the software 3) Seek support?
- [ ] **References:** When present, do references in the text use an appropriate citation method?

### Functionality

- [ ] **Installation:** Does installation succeed as outlined in the documentation?
- [ ] **Functionality:** Have the functional claims of the software been confirmed?
- [ ] **Performance:** If there are any performance claims of the software, have they been confirmed? (If there are no claims, please check off this item.)
- [ ] **Automated tests:** If there are unit tests, do they cover essential functions of the software and a reasonable range of inputs and conditions? Do all tests pass when run locally? (If there are no tests, as in the case of a collection of notebooks, please check off this item.)

### Reviewer checklist source statement

This checklist utilizes elements of the Journal of Open Source Science (JOSS) review [checklist](https://joss.readthedocs.io/en/latest/review_checklist.html): it has been modified for use with USGS software releases.
