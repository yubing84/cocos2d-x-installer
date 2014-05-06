//
//  AndroidPathsPane.h
//  AndroidPaths
//
//  Created by zhangbin on 14-5-4.
//  Copyright (c) 2014年 cocos2d-x. All rights reserved.
//

#import <InstallerPlugins/InstallerPlugins.h>

@interface AndroidPathsPane : InstallerPane
{
    IBOutlet NSTextField * sdkPath;
    IBOutlet NSTextField * ndkPath;

    IBOutlet NSButton * btnSdkSelct;
    IBOutlet NSButton * btnNdkSelct;

    IBOutlet NSButton * btnSkip;
}

- (IBAction) pathSelect:(id)aBtn;
- (IBAction) skipClicked:(id)aBtn;

@end
