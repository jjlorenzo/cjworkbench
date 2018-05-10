import React from 'react'
import WorkflowNavBar from './WorkflowNavBar'
import { shallow, mount, ReactWrapper } from 'enzyme'
const Utils = require('./utils');
import { jsonResponseMock, okResponseMock } from './utils'


describe('WorkflowNavBar', () => {
  let wrapper;
  let user;
  let workflow;
  const mockWorkflowCopy = {
    id: 77,
    name: 'Copy of Original Version',
    owner_name: 'Paula Plagarizer',
    public: false
  };
  const api = {
    duplicateWorkflow: jsonResponseMock(mockWorkflowCopy),
    setWorkflowPublic: okResponseMock()
  };

  afterEach(() => wrapper.unmount())

  let globalGoToUrl
  beforeEach(() => {
    globalGoToUrl = Utils.goToUrl
    Utils.goToUrl = jest.fn()
  })
  afterEach(() => {
    Utils.goToUrl = globalGoToUrl
  })

  it('With user logged in, Duplicate button sends user to new copy', (done) => {
    user = {
      id: 8
    };
    workflow = {
      name: 'Original Version',
      owner_name: 'John Johnson',
      public: true
    };

    Utils.goToUrl = jest.fn();

    wrapper = mount(
      <WorkflowNavBar
        workflow={workflow}
        api={api}
        isReadOnly={false}
        loggedInUser={user}
      />
    );

    expect(wrapper).toMatchSnapshot(); 
    expect(wrapper.state().spinnerVisible).toBe(false);

    let button = wrapper.find('.test-duplicate-button');
    expect(button).toHaveLength(1);
    button.first().simulate('click');

    // spinner starts immediately
    expect(wrapper.state().spinnerVisible).toBe(true);
    
    // then we wait for promise to resolve
    setImmediate( () => {
      // no snapshot test here: 
      //  we have not actually rendered the new workflow copy, just mocked the calls to change url
      expect(Utils.goToUrl).toHaveBeenCalledWith('/workflows/77')
      expect(api.duplicateWorkflow).toHaveBeenCalled()
      done();
    });
  });
  
  it('With user NOT logged in, Duplicate button sends user to sign-in page', (done) => {
    workflow = {
      id: 303,
      name: 'Original Version',
      owner_name: 'Not LogggedIn',
      public: true
    };

    wrapper = mount(
      <WorkflowNavBar
        workflow={workflow}
        api={api}
        isReadOnly={false}      // no loggedInUser prop
      />
    );

    expect(wrapper).toMatchSnapshot(); 

    let button = wrapper.find('.test-duplicate-button');
    expect(button).toHaveLength(1);
    button.simulate('click');

    // wait for promise to resolve
    setImmediate( () => {
      // no snapshot test here: 
      //  we have not actually rendered the sign in page, just mocked the calls to change url
    
      // goToUrl() called once previously
      expect(Utils.goToUrl).toHaveBeenCalledWith('/account/login')
      // check that API was NOT called (has one call from last test)
      expect(api.duplicateWorkflow.mock.calls.length).toBe(1);
      done();
    });

  });

  it('In Private mode, Share button invites user to set to Public', (done) => {
    user = {
      id: 99
    };
    workflow = {
      id: 808,
      name: 'Original Version',
      owner_name: 'Fred Frederson',
      public: false,
    };

    wrapper = mount(
      <WorkflowNavBar
        workflow={workflow}
        api={api}
        isReadOnly={false}
        loggedInUser={user}
      />
    );

    expect(wrapper).toMatchSnapshot();
    expect(wrapper.state().modalsOpen).toBe(false);
    
    let button = wrapper.find('.test-share-button');
    expect(button).toHaveLength(1);
    button.simulate('click');

    expect(wrapper.state().modalsOpen).toBe(true);      

    // FIXME upgrade to React v16 and reactstrap v5 and uncomment
    done()
    //// The insides of the Modal are a "portal", that is, attached to root of DOM, not a child of Wrapper
    //// So find them, and make a new Wrapper
    //// Reference: "https://github.com/airbnb/enzyme/issues/252"
    //let setpubModalElement = document.getElementsByClassName('test-setpublic-modal');
    //let setpubModal = new ReactWrapper(setpubModalElement[0], true)

    //expect(setpubModal).toMatchSnapshot(); 

    //let setPublicButton = setpubModal.find('.test-public-button');
    //expect(setPublicButton.length).toBe(1);
    //setPublicButton.simulate('click');

    //// wait for promise to resolve
    //setImmediate( () => {
    //  wrapper.update()
    //  // find the Share modal & wrap it
    //  let shareModalElement = document.getElementsByClassName('test-share-modal');
    //  let shareModal = new ReactWrapper(shareModalElement[0], true)

    //  expect(shareModal).toMatchSnapshot(); 
    //
    //  // check that link has rendered correctly
    //  let linkField = shareModal.find('.test-link-field');
    //  expect(linkField.length).toBe(1);
    //  // Need to fix this once correct link string in place
    //  // expect(linkField.props().placeholder).toEqual("");
    //
    //  expect(api.setWorkflowPublic.mock.calls.length).toBe(1);
    //  done();
    //});

  });


  it('In Public mode, Share button opens modal with links', () => {
    user = {
      id: 47
    };
    workflow = {
      id: 808,
      name: 'Original Version',
      owner_name: 'Fred Frederson',
      public: true,
    };
    wrapper = mount(
      <WorkflowNavBar
        workflow={workflow}
        api={api}
        isReadOnly={false}
        loggedInUser={user}
      />
    );

    expect(wrapper).toMatchSnapshot();
    expect(wrapper.state().modalsOpen).toBe(false);
    
    let button = wrapper.find('.test-share-button');
    expect(button).toHaveLength(1);
    button.simulate('click');

    expect(wrapper.state().modalsOpen).toBe(true);      

    // FIXME Upgrade to React v16 and reactstrap v5 and uncomment
    //// The insides of the Modal are a "portal", that is, attached to root of DOM, not a child of Wrapper
    //// So find them, and make a new Wrapper
    //// Reference: "https://github.com/airbnb/enzyme/issues/252"
    //let shareModalElement = document.getElementsByClassName('test-share-modal');
    //let shareModal = new ReactWrapper(shareModalElement[0], true)

    //expect(shareModal).toMatchSnapshot(); 

    //// check that link has rendered correctly
    //let linkField = shareModal.find('.test-link-field');
    //expect(linkField.length).toBe(1);
    //expect(linkField.props().placeholder).toEqual("/workflows/808");
  
    //// no extra calls to API expected, 1 from last test
    //expect(api.setWorkflowPublic.mock.calls.length).toBe(1);
  });
});