//
//  AndroidPathsPane.m
//  AndroidPaths
//
//  Created by zhangbin on 14-5-4.
//  Copyright (c) 2014年 cocos2d-x. All rights reserved.
//

#import "AndroidPathsPane.h"

@implementation AndroidPathsPane

NSString* scriptPath = @"/Applications/cocos/cocos2d-x/setup.py";
BOOL skipClicked = NO;

- (void)didEnterPane:(InstallerSectionDirection)aDir
{
    // initialize the following outlet fields
    NSString* sdkPathValue = [self getValueOf:@"ANDROID_SDK_ROOT"];
    NSString* ndkPathValue = [self getValueOf:@"NDK_ROOT"];

    [sdkPath setStringValue:sdkPathValue];
    [ndkPath setStringValue:ndkPathValue];
    
    NSDate * now = [NSDate date];
    NSDateFormatter *fmt = [[NSDateFormatter alloc] init];
    fmt.dateStyle = kCFDateFormatterMediumStyle;
    fmt.timeStyle = kCFDateFormatterShortStyle;
    NSString *newDateString = [fmt stringFromDate:now];
    [self installLog:""];
    [self installLog:[newDateString UTF8String]];

    // disable the Continue button
    [self setNextEnabled:YES];
    
    // disable the Go Back button
    [self setPreviousEnabled:NO];
}

- (void)willExitPane:(InstallerSectionDirection)aDir
{
    [self installLog:"will exit pane invoked!"];
    NSString* sdkPathValue = @" ";
    NSString* ndkPathValue = @" ";
    if (! skipClicked) {
        sdkPathValue = [sdkPath stringValue];
        ndkPathValue = [ndkPath stringValue];
    }

    // run python script to setup the environment
    NSArray* args = [NSArray arrayWithObjects:scriptPath, @"-n", ndkPathValue, @"-a", sdkPathValue, nil];
    BOOL bRet = [self runPython:args];
    if (!bRet) {
        // run python script failed, raise dialog
        [self installLog:"Run python script failed!"];
        NSAlert *alert = [[NSAlert alloc] init];
        [alert addButtonWithTitle:@"OK"];
        [alert setMessageText:@"Setup environment failed!"];
        [alert setInformativeText:[NSString stringWithFormat:@"Python is required, you can run the scipt %@ manually later!", scriptPath]];
        [alert setAlertStyle:NSWarningAlertStyle];
        [alert runModal];
    }
}

- (BOOL)shouldExitPane:(InstallerSectionDirection)aDir
{
    [self installLog:"should exit pane invoked!"];
    if (skipClicked) {
        return YES;
    }

    BOOL bRet = NO;
    NSString* sdkPathValue = [sdkPath stringValue];
    NSString* ndkPathValue = [ndkPath stringValue];
    NSString* checkSdkFile = [NSString stringWithFormat:@"%@/tools/android", sdkPathValue];
    NSString* checkNdkFile = [NSString stringWithFormat:@"%@/ndk-build", ndkPathValue];

    NSString* tipMsg = nil;
    do {
        NSFileManager* fileManager = [NSFileManager defaultManager];
        if (! [fileManager fileExistsAtPath:checkSdkFile])
        {
            tipMsg = [NSString stringWithFormat:@"%@ is not a valid Android SDK path", sdkPathValue];
            break;
        }

        if (! [fileManager fileExistsAtPath:checkNdkFile])
        {
            tipMsg = [NSString stringWithFormat:@"%@ is not a valid NDK path", ndkPathValue];
            break;
        }
        
        bRet = YES;
    } while (0);

    if (! bRet) {
        // raise dialog
        [self installLog:"Check path value failed : %s!", [tipMsg UTF8String]];
        NSAlert *alert = [[NSAlert alloc] init];
        [alert addButtonWithTitle:@"OK"];
        [alert setMessageText:@"Check the paths failed!"];
        [alert setInformativeText:tipMsg];
        [alert setAlertStyle:NSWarningAlertStyle];
        [alert runModal];
    }

    return bRet;
}

- (NSString *)title
{
	return [[NSBundle bundleForClass:[self class]] localizedStringForKey:@"PaneTitle" value:nil table:nil];
}

- (IBAction) pathSelect:(id)aBtn
{
    NSTextField* relateField = nil;
    if (aBtn == btnNdkSelct)
    {
        relateField = ndkPath;
    }
    else if (aBtn == btnSdkSelct)
    {
        relateField = sdkPath;
    }

    if (nil == relateField)
    {
        return;
    }

    NSOpenPanel *panel = [NSOpenPanel openPanel];
    [panel setCanChooseFiles:NO];
    [panel setCanChooseDirectories:YES];
    [panel setAllowsMultipleSelection:NO];
    
    NSInteger clicked = [panel runModal];
    
    if (clicked == NSFileHandlingPanelOKButton) {
        for (NSURL *url in [panel URLs]) {
            NSString* strPath = [url path];
            [relateField setStringValue:strPath];
        }
    }
}

- (IBAction) skipClicked:(id)aBtn
{
    [self installLog:"skip clicked!"];
    skipClicked = YES;

    // goto the next step
    [self gotoNextPane];
}

- (NSString*) getPythonPath
{
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:@"/usr/bin/which"];
    NSPipe *pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
    [task setArguments:[NSArray arrayWithObject:@"python"]];

    [task launch];
    [task waitUntilExit];
    
    int status = [task terminationStatus];
    if (status != 0) {
        // failed to get the python path
        [self installLog:"get python path failed!"];
        return nil;
    }

    NSFileHandle *file = [pipe fileHandleForReading];
    NSData *data = [file readDataToEndOfFile];
    NSString *string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
    
    return string;
}

- (BOOL) runPython:(NSArray*) args
{
    NSString* pythonPath = [self getPythonPath];
    if (pythonPath == nil) {
        // failed to get the python path
        return NO;
    }

    pythonPath = [pythonPath stringByReplacingOccurrencesOfString:@"\n" withString:@""];
    [self installLog:"python path is : %s", [pythonPath UTF8String]];
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:pythonPath];
    NSPipe *pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
    [task setArguments:args];

    [task launch];
    [task waitUntilExit];
    int status = [task terminationStatus];

    [self installLog:"Return code of running python script: %d", status];
    if (status == 0)
    {
        return YES;
    }
    else
    {
        NSFileHandle *file = [pipe fileHandleForReading];
        NSData *data = [file readDataToEndOfFile];
        NSString *string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
        [self installLog:"Output of python script: %s", [string UTF8String]];
        return NO;
    }
}

- (NSString *) getValueOf:(NSString *) var
{
    
    NSString* strRet = [[[NSProcessInfo processInfo]environment]objectForKey:var];

//    NSTask *task = [[NSTask alloc] init];
//    [task setLaunchPath:@"/bin/sh"];
//    NSPipe *pipe = [NSPipe pipe];
//    [task setStandardOutput: pipe];
//    
//    NSString* varStr = [NSString stringWithFormat:@"${%@}", var];
//    [task setArguments:[NSArray arrayWithObjects:varStr, nil]];
//    [task launch];
//    [task waitUntilExit];
////    int status = [task terminationStatus];
////    [self writeUsingC:"get value of %@ ret: %d", var, status]];
//
//    NSFileHandle *file = [pipe fileHandleForReading];
//    NSData *data = [file readDataToEndOfFile];
//    NSString *string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];

    if (nil == strRet) {
        strRet = @"";
    }

    [self installLog:"value of %s is : %s", [var UTF8String], [strRet UTF8String]];
    return strRet;
}

- (const char*) getLogFilePath
{
    NSString* homePath = NSHomeDirectory();
    NSString* retPath = [NSString stringWithFormat:@"%@/.cocos2d", homePath];
    NSString* retFilePath = [NSString stringWithFormat:@"%@/install-log.txt", retPath];
    NSFileManager* fileManager = [NSFileManager defaultManager];
    if (! [fileManager fileExistsAtPath:retFilePath]) {
        [fileManager createDirectoryAtPath:retPath withIntermediateDirectories:YES attributes:nil error:nil];
        [fileManager createFileAtPath:retFilePath contents:nil attributes:nil];
    }

    return [retFilePath UTF8String];
}

- (void) installLog:(const char *) format,...
{
    va_list list;
    va_start(list, format);
    
    char buf[1024];
    vsnprintf(buf, 1021, format, list);
    strcat(buf, "\n");

    FILE *fp = fopen([self getLogFilePath],"a");
    fprintf(fp, "%s", buf);
    fclose(fp);

    va_end(list);
}

@end
